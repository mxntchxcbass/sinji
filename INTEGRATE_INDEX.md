# 앱 연결 패치

새 은행은 `extra.json`의 `x1` pool로 읽히며, `question_factory.js`는 앱 내부의 5개 `AREA_DEFS` 생성기를 교체합니다. 기존 `index.html` 파일 끝에서 `</body>` 앞에 다음 태그를 추가해야 앱이 새 생성기를 불러옵니다.

```html
<script src="./question_factory.js"></script>
```

기존 상단 고지 문구도 다음처럼 바꾸세요.

```html
<div class="disclaimer">이 연습실은 SKCT 공개 유형 안내와 참고 자료의 유형·시간 압박 특성을 바탕으로 새로 작성한 연습 문항을 제공합니다. 교재·유료 모의고사 문항을 복제하지 않으며, 실제 시험과 동일한 문항 또는 난도를 보장하지 않습니다.</div>
```

`question_factory.js`가 로드되면 위 고지 문구와 영역별 설명을 자동으로 설정합니다. 직접 테스트하려면 `node test_question_bank.js`, `python -m unittest test_generate_extra.py`를 실행하고, 은행을 다시 만들려면 `python generate_extra.py --seed 20261002 --count 10`을 실행하세요.
