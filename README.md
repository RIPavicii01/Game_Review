# 🎮 Nintendo Switch 게임 리뷰 감정 분석 프로젝트

## 🎯 프로젝트 목표

게임을 구매할 때 숫자 평점만 믿고 선택해도 괜찮을까?  
텍스트로 작성된 리뷰의 실제 감정과 점수 평가 사이에는 과연 일관성이 있을까?

이 프로젝트는 이런 질문에서 출발했다.  
Metacritic 웹사이트는 다양한 게임 리뷰를 **숫자 점수(0~100)**와 **텍스트 리뷰** 두 가지 방식으로 제공한다. 하지만 때때로 **점수는 높지만 부정적인 내용을 담은 리뷰**나, 반대로 **점수는 낮지만 긍정적인 분위기의 리뷰**도 발견된다.

따라서 본 프로젝트에서는 사용자 및 평론가의 텍스트 리뷰를 기반으로 감정을 분석하고, **텍스트의 실제 감정(긍정/부정)**이 점수와 얼마나 일치하는지를 확인하고자 했다.  
이를 통해 단순 숫자 평점 외에도, 텍스트 분석이 게임 리뷰의 해석에 얼마나 유의미한 정보를 줄 수 있는지를 보여주는 것이 핵심 목표다.

---

## 🛠 사용 기술

- ![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white): 데이터 수집 및 전처리, 모델 학습 전반
- ![Selenium](https://img.shields.io/badge/Selenium-Automation-green?logo=selenium&logoColor=white): 리뷰 자동 크롤링
- ![PyTorch](https://img.shields.io/badge/PyTorch-Deep_Learning-EE4C2C?logo=pytorch&logoColor=white): 딥러닝 모델 학습
- ![Transformers](https://img.shields.io/badge/Transformers-HuggingFace-yellow?logo=huggingface&logoColor=black): 사전 학습된 언어 모델 활용

---

## 📥 데이터 수집 및 전처리

Metacritic에서 닌텐도 스위치 전용 게임들의 리뷰를 수집하기 위해, Selenium과 크롬 드라이버를 활용해 크롤러를 구현했다.  
해당 웹사이트는 동적으로 구성되어 있어서, 일반적인 정적 크롤링 방법으로는 데이터 수집이 어려웠다.  

- **사용자 리뷰**는 페이지 하단으로 스크롤을 반복해서 로딩되는 구조였기 때문에, 자동 스크롤을 통해 모든 리뷰를 확보했다.  
- **평론가 리뷰**는 페이지 이동 버튼을 자동으로 클릭하면서 데이터를 순차적으로 수집했다.

이 과정을 통해 총 2,000개의 영어 리뷰를 확보했다.  
다만 닌텐도 스위치 게임 리뷰의 특성상 **최고 점수(10점)**을 부여한 긍정 리뷰가 압도적으로 많았기 때문에, 학습 데이터가 편향되지 않도록 긍/부정 비율을 균형 있게 조절했다.

---

![데이터 수집 과정](1.png)

---

## 🧠 모델 학습 (DeBERTa 기반)

감정 분석을 위해 **Microsoft의 사전학습 언어 모델 DeBERTa v3 Small**을 기반으로 파인튜닝을 진행했다.  
라벨은 이진 분류(binary classification)로 설정하여, 감정이 **긍정(1)**인지 **부정(0)**인지를 예측하도록 했다.

### 🔎 긍정 리뷰의 특징
- **칭찬 어휘 사용**: `best`, `love`, `great`, `excellent`, `masterpiece`, `amazing`, `fantastic`, `awesome`, `fun`
- **추천 표현 포함**: `"must play"`, `"I recommend"`, `"you should try"`
- **감탄 및 강조 표현**: `!`, `really`, `absolutely`

### ⚠️ 부정 리뷰의 특징
- **비판적 어휘 사용**: `boring`, `worst`, `bad`, `disappointed`, `underwhelming`, `awful`, `terrible`
- **불만 표현**: `"I regret"`, `"waste of time"`, `"not fun"`, `"no point"`
- **강조 표현**: `really bad`, `completely boring`

---

## 📁 프로젝트 폴더 구조

```plaintext
Game_review/
├── .venv/                            # 가상환경
├── chromedriver-win64/              # 크롤링용 드라이버
│   └── chromedriver.exe
├── deberta_custom_model_metacritic/ # 학습된 모델 저장 경로
│   ├── config.json
│   ├── model.safetensors
│   ├── tokenizer_config.json
│   └── ...
├── all_metacritic_reviews1~3.csv    # 리뷰 원본 백업 데이터
├── metacritic_review.csv            # 크롤링된 전체 리뷰 데이터
├── metacritic_review_labeled.csv    # 라벨링 완료된 학습용 데이터
├── fine_tuned_DeBERTa.py            # DeBERTa 학습 스크립트
├── main2.py                         # 예측 및 검증용 실행 파일
├── datadownload.py                 # 크롤링 스크립트
└── README.md
```


---

## ✅ 모델 성능

- 검증 데이터셋 기준 **정확도: 78%**
- 학습된 모델은 `deberta_custom_model_metacritic/` 경로에 저장되어 있으며, 이후 다양한 리뷰 데이터에 적용 가능하다.

---

## 😕 한계점 및 개선 방향

### ❗ 한계점

- 리뷰 데이터 중 일부가 영어 외 언어로 작성되어, 모델 예측이 불안정할 가능성이 존재한다.
- 본래는 **긍정 / 부정** 외에도 **중립(애매한 감정)** 클래스를 추가하고자 했으나, 다음과 같은 이유로 구현하지 못했다:
  1. **중립**을 정의하는 기준이 명확하지 않았고,
  2. 많은 게임 리뷰가 긍정적인 표현과 부정적인 표현을 **동시에 포함**하고 있어, **긍정도 부정도 아닌 '중간' 상태로 분류될 수밖에 없는 리뷰가 매우 많았다**.

  이로 인해 실제 분류 기준이 모호해지고, 학습 시 혼동을 유발하는 문제가 발생했기 때문에 최종적으로는 **이진 분류(긍정/부정)**만 적용했다.
- 긍정 리뷰가 많은 데이터셋임에도 불구하고 정확도가 높지 않았다는 점은 모델 구조나 학습 전략에 개선 여지가 있음을 의미한다.

### 🔧 개선 방향

- 언어 감지 기능을 도입하여 **영어 리뷰만 필터링**하는 전처리 강화
- **중립 클래스 추가** 및 기준 정의를 통해 **3클래스 분류(Multi-class classification)**로 확장
- 데이터 불균형을 해소하기 위해 **EDA(Easy Data Augmentation)**와 같은 **데이터 증강 기법** 도입
- 단순 텍스트 외에 **메타데이터(점수, 작성일 등)**를 함께 고려하는 **멀티모달 학습**으로 정밀도 향상 가능

---

## 🔚 결론

이번 프로젝트를 통해 감정 분석 모델이 숫자 점수만으로는 파악하기 어려운 리뷰의 **정서적 뉘앙스를 효과적으로 포착**할 수 있다는 가능성을 확인했다.  
특히 게임과 같은 주관적인 경험에 있어 텍스트 분석은 점수 이상의 정보를 제공하며, **사용자 만족도나 콘텐츠 평가의 정확도**를 높이는 데 기여할 수 있다.

향후에는 다양한 플랫폼과 장르에 대한 리뷰를 분석하고, 정교한 멀티클래스 모델 및 멀티모달 방식으로 확장해 **보다 정밀한 감정 인식 시스템 구축**을 목표로 할 수 있다.  
감정 분석 기술은 단순한 데이터 분류를 넘어 **실제 사용자 경험을 이해하는 도구**로 충분히 활용 가능하다는 점에서 의미 있는 도전이었다.
