import numpy as np
import os
from keras.models import load_model

# 모델 load
model = load_model(os.path.abspath(os.path.dirname(__file__))+'/Models/model.h5')
# 제스처 종류
actions = ['a', 'b', 'c']
# 데이터 시퀀스 길이, 녹화시간
seqLength = 10

angleData = []
actionPredicted = []

# result는 [[x,y,z]....] 형식

def recognizeGesture(result):
# 손 있을 때
    for i in range(result):
        # 랜드마크 좌표
        lm_coordinates = np.zeros((21, 3))
        lm_coordinates[i] = [float(result[i][0]), float(result[i][1]), float(result[i][2])]
            
        # 벡터를 이용한 랜드마크간 각도 계산
        a1 = lm_coordinates[[0,1,2,3,0,5,6,7,0, 9,10,11, 0,13,14,15, 0,17,18,19], :]
        a2 = lm_coordinates[[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], :]
        v = a2 - a1
        # 단위벡터로 표준화 normalize
        v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]    # 내적할 수 있게 열 벡터로
        # 내적을 이용한 각도 계산 ( a•b = |a||b|cos(Θ) )
        angle = np.arccos(np.einsum('nt,nt->n',     # 내적, cos의 역수
            v[[0,1,2,4,5,6,8, 9,10,12,13,14,16,17,18],:], 
            v[[1,2,3,5,6,7,9,10,11,13,14,15,17,18,19],:]))
        # 라디안 단위 변환
        angle = np.degrees(angle)
        # 데이터 구성
        angleData.append(angle)

    ## 판단
        # 설정한 시퀀스길이만큼 데이터 생겨야 판단
        if len(angleData) < seqLength:
            continue

        # 설정한 시퀀스길이만큼의 데이터를 문제지로
        Xdata = np.expand_dims(np.array(angleData[-seqLength:]), axis=0)
        # 라벨별 예측 확률
        Yprobabilities = model.predict(Xdata).squeeze()
        # 가장 확률 높은 라벨
        Yindex = int(np.argmax(Yprobabilities))
        # 그 라벨의 확률
        confidence = Yprobabilities[Yindex]

        # 특정 확률 이상일 때
        if confidence < 1:
            continue

        action = actions[Yindex]
        actionPredicted.append(action)
        if len(actionPredicted) < 3:
            continue
        # 특정 횟수만큼 같은 동작이라고 판단되면
        predictedAs = ''
        if actionPredicted[-1] == actionPredicted[-2] == actionPredicted[-3]:
            predictedAs = action

    return predictedAs