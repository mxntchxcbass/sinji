#!/usr/bin/env python3
"""Generate fresh, original SKCT-style practice items for sinji/extra.json.

The site already loads extra.json as BANK.x1 and samples it through its native
random question flow. This script writes questions in that exact schema.
No third-party packages are required.
"""
import argparse
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "extra.json"
AREAS = ("lang", "data", "math", "logic", "seq")
AREA_NAMES = {"lang": "언어이해", "data": "자료해석", "math": "창의수리", "logic": "언어추리", "seq": "수열추리"}
SOURCE = "창작 연습문항 · 공개 학습자료의 유형 분류 참고 · 공식 기출 아님"


def mc(q, choices, answer, explanation, area, skill, difficulty, passage=None, figure=None, topic=""):
    assert len(choices) == 5 and len(set(choices)) == 5, (q, choices)
    assert 0 <= answer < 5
    item = {"area": area, "q": q, "p": passage or [], "c": choices, "a": answer, "e": explanation,
            "_meta": {"skill": skill, "difficulty": difficulty, "topic": topic, "source_basis": SOURCE}}
    if figure:
        item["g"] = [figure]
    return item


def rotate_options(rng, options, correct):
    """Shuffle choice order while returning the matching zero-based answer index."""
    pairs = list(enumerate(options))
    rng.shuffle(pairs)
    out = [text for _, text in pairs]
    return out, next(i for i, (old_i, _) in enumerate(pairs) if old_i == correct)


def lang_items(rng):
    data = [
      ("기술 도입과 성과", "한 물류센터는 자동 분류 장비를 도입한 뒤 처리량이 증가했다. 하지만 같은 시기에 주문량과 근무 인원도 늘었다. 장비의 효과를 따로 확인하려면 주문량과 인원 변화가 비슷한 기간 또는 센터와 비교할 필요가 있다.", "글의 핵심으로 가장 적절한 것은?", ["장비 도입 뒤 처리량 증가는 모두 장비 효과다.", "장비 효과를 평가할 때 함께 변한 요인을 통제해야 한다.", "주문량이 늘면 자동 장비는 필요하지 않다.", "근무 인원은 처리량과 무관하다.", "센터 간 성과 비교는 불가능하다."], 1, "동시에 변한 요인을 분리하지 않고 장비 효과라고 단정할 수 없다."),
      ("재활용 지표", "폐배터리 회수량은 늘었지만 재사용 가능한 소재의 회수율은 크게 달라지지 않았다. 회수된 배터리 중에는 파손되거나 분류가 어려운 제품도 있고, 회수 후 분해·정제할 수 있는 시설 용량에도 한계가 있다. 따라서 회수량만으로 자원 순환 성과를 판단하기 어렵다.", "글에서 반드시 따라오는 결론은?", ["회수량이 늘면 재사용 소재량도 같은 비율로 늘어난다.", "시설 용량은 자원 순환 성과와 무관하다.", "회수량만으로 실제 자원 순환 성과를 단정하기 어렵다.", "파손 배터리는 모두 재활용된다.", "배터리 회수 사업은 중단해야 한다."], 2, "회수와 실제 재사용 가능 소재의 회수를 구분하므로 회수량만으로 성과를 판단할 수 없다."),
      ("표본 대표성", "한 기업이 신제품 만족도를 조사하기 위해 온라인 응답자 300명을 모집했다. 응답자 대부분은 해당 기업의 기존 고객이었다. 조사 결과는 응답 고객의 만족도를 보여 주지만, 제품을 처음 접할 사람들의 반응까지 그대로 나타낸다고 보기는 어렵다.", "조사 결과의 한계로 가장 적절한 것은?", ["응답자가 300명이므로 어떤 결론도 낼 수 없다.", "기존 고객 중심 표본을 전체 잠재 고객으로 일반화하기 어렵다.", "온라인 설문은 만족도를 측정할 수 없다.", "기존 고객의 의견은 신제품 평가에 쓸 수 없다.", "만족도는 제품 성능과 항상 반대 방향이다."], 1, "표본 구성과 일반화 대상이 달라 대표성에 한계가 있다."),
      ("품질 개선", "불량이 발생했을 때 작업자에게 주의만 당부하면 같은 문제가 반복될 수 있다. 공정 조건, 원재료 편차, 설비 상태와 검사 기준을 함께 확인해야 원인을 찾을 수 있다. 재발 방지를 위해서는 원인에 대응하는 공정 기준과 확인 절차를 남겨야 한다.", "글의 주장으로 가장 적절한 것은?", ["불량은 작업자의 부주의에서만 생긴다.", "재발 방지는 원인 검증과 공정 기준 개선을 함께 해야 한다.", "검사 기준은 불량 분석에 사용할 수 없다.", "주의 교육을 반복하면 공정 개선은 필요 없다.", "불량은 기록하지 않는 편이 낫다."], 1, "사람을 탓하는 데 그치지 않고 여러 공정 요인을 검증해 기준으로 연결해야 한다."),
      ("예측 모델", "수요 예측 모델의 평균 오차가 낮더라도 특정 계절이나 제품군에서 오차가 집중될 수 있다. 재고 의사결정에서는 전체 평균뿐 아니라 제품군별 오차와 과소 예측의 비용도 살펴야 한다.", "글의 관점과 일치하는 것은?", ["평균 오차가 낮으면 모든 제품군의 예측도 정확하다.", "전체 평균만으로 재고 의사결정을 해도 충분하다.", "제품군별 오차와 예측 방향의 비용을 함께 봐야 한다.", "과소 예측은 재고에 영향을 주지 않는다.", "예측 모델은 의사결정에 이용할 수 없다."], 2, "평균이 가릴 수 있는 집단별 오차와 과소 예측 비용을 함께 살펴야 한다."),
      ("디지털 접근성", "행정 서비스를 온라인으로 전환하면 처리 시간과 이용 편의가 개선될 수 있다. 그러나 기기나 네트워크를 이용하기 어렵거나 화면을 이해하기 힘든 사람은 서비스에서 배제될 수 있다. 전환 성과를 평가할 때는 편의와 접근성을 함께 확인해야 한다.", "글의 중심 내용은?", ["온라인 행정 서비스는 반드시 폐지해야 한다.", "디지털 전환은 처리 속도만으로 평가해야 한다.", "온라인 전환의 편의와 이용자 접근성을 함께 평가해야 한다.", "모든 이용자는 같은 수준으로 디지털 기기를 쓴다.", "대면 서비스는 온라인보다 항상 빠르다."], 2, "온라인 전환의 이점과 접근성 위험을 함께 평가하자는 주장이다."),
      ("공급망 재고", "재고를 줄이면 보관 비용을 낮출 수 있지만, 공급이 지연될 때 생산 중단 위험은 커진다. 공급업체의 납기 변동, 대체 자재의 확보 가능성, 생산 중단 비용을 함께 고려해 품목별 안전 재고를 정하는 것이 바람직하다.", "가장 타당한 결론은?", ["모든 품목의 재고를 같은 비율로 줄여야 한다.", "보관 비용만 고려해 재고를 최소화해야 한다.", "공급 위험과 중단 비용을 반영해 품목별 재고 기준을 정해야 한다.", "공급 지연은 재고 수준과 무관하다.", "대체 자재가 있으면 안전 재고는 필요 없다."], 2, "비용 절감과 공급 중단 위험 간 균형을 품목별로 설정해야 한다."),
      ("실험 설계", "새 교육 프로그램 참여자의 성적이 올랐다는 사실만으로 프로그램의 효과를 확정하기는 어렵다. 참여자가 자발적으로 신청했다면 원래 학습 의지가 높았을 수 있기 때문이다. 비슷한 조건의 비참여 집단과 변화량을 비교하면 효과를 더 잘 판단할 수 있다.", "프로그램 효과 검증을 강화하는 방법은?", ["참여자의 사후 점수만 확인한다.", "자발적 참여 여부를 무시한다.", "비슷한 조건의 비교 집단과 전후 변화량을 비교한다.", "성적이 오른 사람만 분석에서 남긴다.", "교육 만족도만으로 성적 효과를 확정한다."], 2, "자기 선택 편향을 줄이려면 비교 가능한 집단의 변화량을 함께 보아야 한다."),
      ("정보 공개", "제품 환경 표시가 소비자 선택에 도움이 되려면 산정 기준과 단위를 알기 쉬워야 한다. 기업마다 서로 다른 기준을 쓰면 숫자가 있어도 제품 간 비교가 어려울 수 있다. 공통 기준과 검증 절차는 표시의 신뢰성을 높인다.", "글에서 추론할 수 있는 내용은?", ["수치 정보가 있으면 기준 차이는 중요하지 않다.", "공통 산정 기준은 제품 간 비교를 돕는다.", "환경 표시는 소비자 선택에 영향을 줄 수 없다.", "검증 절차는 표시 신뢰성과 무관하다.", "기업별 표시 기준은 다를수록 비교가 쉽다."], 1, "공통 단위와 기준이 서로 다른 제품의 비교 가능성을 높인다."),
      ("결측 데이터", "설비 센서 기록에 빈칸이 발견되었다. 통신 오류 때문에 생긴 누락과 특정 운전 상태에서 센서가 측정하지 않아 생긴 누락은 의미가 다를 수 있다. 분석 전에 결측이 발생한 조건을 확인하지 않으면 정상 상태와 고장 징후를 혼동할 수 있다.", "분석 전에 우선 확인해야 할 것은?", ["빈칸을 모두 0으로 바꾸는 일", "누락이 발생한 조건과 원인", "결측이 있는 행을 전부 삭제하는 일", "설비 이름의 가나다순", "결측 비율이 0%가 되도록 값을 임의로 채우는 일"], 1, "누락 메커니즘을 파악해야 값의 의미를 적절히 처리할 수 있다.")
    ]
    out=[]
    for i,(topic,pas,q,choices,ans,exp) in enumerate(data,1):
        opts,idx=rotate_options(rng,choices,ans)
        diff=("기초","표준","도전")[(i-1)%3]
        out.append(mc(q,opts,idx,exp,"lang",("중심 내용","내용 추론","근거 평가")[i%3],diff,[pas],topic=topic))
    return out


def table_figure(title, headers, rows, unit):
    return {"k":"t","title":title,"unit":unit,"h":[headers],"r":rows}


def data_items(rng):
    out=[]
    # Six synthetic production datasets, each yielding a distinct weighted-rate or share question.
    for i in range(6):
        labels=rng.sample(["가공","조립","검사","포장","성형","도장","물류","정비"],3)
        productions=[rng.randrange(5,14)*100 for _ in range(3)]
        rates=[rng.randrange(10,51)/10 for _ in range(3)]
        rows=[[labels[j],f"{productions[j]:,}",f"{rates[j]:.1f}%"] for j in range(3)]
        fig=table_figure("사업장별 생산 현황",["사업장","생산량","불량률"],rows,"개")
        if i%2==0:
            j=rng.randrange(3); total=sum(productions); correct=f"{productions[j]/total*100:.1f}%"
            wrong=[f"{(productions[j]/total*100+d):.1f}%" for d in (5,-5,10,-10)]
            choices,ans=rotate_options(rng,[correct]+wrong,0)
            exp=f"전체 생산량은 {total:,}개이고, {labels[j]} 비중은 {productions[j]:,}÷{total:,}×100={correct}다."
            out.append(mc(f"전체 생산량에서 {labels[j]} 사업장이 차지하는 비중은?",choices,ans,exp,"data","비중 계산",("기초","표준","도전")[i%3],figure=fig,topic="가상 제조 데이터"))
        else:
            total=sum(productions); defects=sum(productions[j]*rates[j]/100 for j in range(3)); val=defects/total*100
            correct=f"{val:.2f}%"; wrong=[f"{max(0,val+d):.2f}%" for d in (0.31,-0.42,0.73,-0.88)]
            choices,ans=rotate_options(rng,[correct]+wrong,0)
            exp=f"불량 수의 합은 생산량×불량률을 사업장별로 계산해 더한 값이다. 이를 전체 생산량 {total:,}개로 나누면 {correct}다."
            out.append(mc("세 사업장의 전체 불량률은?",choices,ans,exp,"data","가중 평균",("기초","표준","도전")[i%3],figure=fig,topic="가상 제조 데이터"))
    # Four trend / comparison questions.
    for i in range(4):
        names=["1분기","2분기","3분기"]
        vals=[rng.randrange(80,151,5),0,0]
        vals[1]=vals[0]+rng.randrange(10,51,5); vals[2]=vals[1]-rng.randrange(5,31,5)
        fig=table_figure("분기별 검사 처리량",["분기","처리량"],[[names[j],str(vals[j])] for j in range(3)],"건")
        if i%2==0:
            v=(vals[1]-vals[0])/vals[0]*100; correct=f"{v:.1f}%"
            wrong=[f"{(v+d):.1f}%" for d in (5,-5,10,-10)]
            choices,ans=rotate_options(rng,[correct]+wrong,0)
            exp=f"증가율은 (2분기−1분기)÷1분기×100이다. ({vals[1]}−{vals[0]})÷{vals[0]}×100={correct}다."
            out.append(mc("1분기 대비 2분기 처리량 증가율은?",choices,ans,exp,"data","증가율",("기초","표준","도전")[i%3],figure=fig,topic="가상 운영 데이터"))
        else:
            correct=f"{sum(vals)/3:.1f}건"; wrong=[f"{sum(vals)/3+d:.1f}건" for d in (5,-5,10,-10)]
            choices,ans=rotate_options(rng,[correct]+wrong,0)
            exp=f"세 분기 처리량 평균은 ({vals[0]}+{vals[1]}+{vals[2]})÷3={correct}다."
            out.append(mc("세 분기의 평균 처리량은?",choices,ans,exp,"data","평균",("기초","표준","도전")[i%3],figure=fig,topic="가상 운영 데이터"))
    return out


def numeric_choices(rng, answer, distractors, unit):
    nums=[]
    for n in [answer]+distractors:
        if n not in nums: nums.append(n)
    delta=1
    while len(nums)<5:
        candidate=answer+delta
        if candidate not in nums: nums.append(candidate)
        delta+=1
    texts=[f"{n:,}{unit}" for n in nums[:5]]
    opts,idx=rotate_options(rng,texts,0)
    return opts,idx


def math_items(rng):
    out=[]
    for i in range(10):
        kind=i%5; difficulty=("기초","표준","도전")[i%3]
        if kind==0:
            a,b=rng.choice([(4,4),(6,3),(8,4),(10,5),(12,6),(12,4)])
            ans=round(a*b/(a+b),2); distract=[a+b,a,b,round(a*b/2,2)]
            opts,idx=numeric_choices(rng,ans,distract,"시간")
            out.append(mc(f"A는 혼자 {a}시간, B는 혼자 {b}시간 걸리는 일을 한다. 두 사람이 함께 하면 몇 시간이 걸리는가?",opts,idx,f"시간당 작업량은 1/{a}+1/{b}다. 함께 하는 시간은 {a}×{b}÷({a}+{b})={ans}시간이다.","math","일률",difficulty,topic="작업 계획"))
        elif kind==1:
            total,frm,to=rng.choice([(200,20,10),(300,20,12),(400,15,10),(500,20,10),(300,15,9),(400,25,10)])
            salt=total*frm/100; added=round(salt/(to/100)-total)
            opts,idx=numeric_choices(rng,added,[added//2,added+total,added+100,max(1,added-100)],"g")
            out.append(mc(f"{frm}% 소금물 {total}g에 물을 더해 {to}% 소금물을 만들려 한다. 물을 몇 g 넣어야 하는가?",opts,idx,f"소금량은 {total}×{frm}%={salt:g}g이다. 최종 용액은 {salt:g}÷{to}%={salt/(to/100):g}g이므로 물은 {added}g이다.","math","농도",difficulty,topic="용액 제조"))
        elif kind==2:
            v=rng.choice([40,50,60,70,80,90]); minutes=rng.choice([30,60,90,120]); ans=v*minutes//60
            opts,idx=numeric_choices(rng,ans,[ans+v//2,max(1,ans-v//2),v+minutes,ans*2],"km")
            out.append(mc(f"시속 {v}km로 {minutes}분 이동했다. 이동 거리는?",opts,idx,f"거리=속력×시간={v}×{minutes}/60={ans}km다.","math","속력·거리·시간",difficulty,topic="운송 경로"))
        elif kind==3:
            n=rng.choice([4,5,6]); ans=3**n-3*2**n+3
            opts,idx=numeric_choices(rng,ans,[3**n,3**n-2**n,ans+3,ans-3],"가지")
            out.append(mc(f"서로 다른 부품 {n}개를 세 조립 키트에 하나씩 배분한다. 모든 키트에 적어도 하나가 들어갈 때 경우의 수는?",opts,idx,f"전체 3^{n}에서 한 키트가 비는 경우 3×2^{n}을 빼고, 두 키트가 비는 경우 3을 더한다. 총 {ans}가지다.","math","경우의 수",difficulty,topic="부품 배분"))
        else:
            price=rng.choice([10000,15000,20000,25000,30000]); disc=rng.choice([10,20,25,30]); tax=rng.choice([0,10]); ans=round(price*(100-disc)/100*(100+tax)/100)
            opts,idx=numeric_choices(rng,ans,[round(price*(100-disc)/100),round(price*(100+tax)/100),ans+1000,max(100,ans-2000)],"원")
            out.append(mc(f"정가 {price:,}원 상품을 {disc}% 할인한 뒤 할인 가격에 {tax}% 세금을 붙였다. 최종 가격은?",opts,idx,f"{price:,}×{(100-disc)/100:.2f}×{(100+tax)/100:.2f}={ans:,}원이다.","math","할인·비용",difficulty,topic="구매 비용"))
    return out


def logic_items(rng):
    raw=[
      ("모든 검사자는 교육을 이수했다. 수연은 검사자다. 반드시 참인 것은?",["수연은 교육을 이수했다.","교육 이수자는 모두 검사자다.","수연은 교육을 진행했다.","검사자가 아닌 사람은 교육을 이수하지 않았다.","수연의 이수 여부는 알 수 없다."],0,"모든 검사자가 교육을 이수했다면 검사자인 수연도 교육을 이수했다.","명제 추리"),
      ("A는 C보다 먼저, D는 B보다 나중에 발표한다. 가능한 순서는?",["C-A-B-D","A-D-C-B","B-A-D-C","D-B-A-C","C-B-D-A"],2,"B-A-D-C는 A가 C보다 앞이고 D가 B보다 뒤라서 조건을 만족한다.","순서 조건"),
      ("P, Q, R, S가 일렬로 선다. P는 Q 바로 앞이고 R은 양 끝에 서지 않는다. 가능한 배열은?",["P-Q-R-S","R-P-Q-S","S-P-Q-R","P-R-Q-S","Q-P-S-R"],0,"P-Q-R-S에서 R은 세 번째이므로 조건을 모두 만족한다.","인접·배치"),
      ("X, Y, Z 중 정확히 두 과제를 한다. X를 하면 Y도 해야 하고 Z를 하면 X는 할 수 없다. 반드시 하는 과제는?",["X","Y","Z","X와 Y","Y와 Z"],1,"가능한 조합은 X·Y 또는 Y·Z다. 두 경우에 공통인 과제는 Y다.","필수 조건"),
      ("세 사람 중 한 명만 참말을 한다. 갑: ‘을이 범인이다.’ 을: ‘나는 범인이 아니다.’ 병: ‘갑은 범인이 아니다.’ 범인은 누구인가?",["갑","을","병","갑 또는 병","알 수 없다"],0,"갑이 범인이면 을의 진술만 참이다. 을 또는 병을 범인으로 두면 참말이 둘이 된다.","진실게임"),
      ("A, B, C 상자에 빨강·파랑·초록 카드가 하나씩 있다. B는 파랑, A는 빨강이 아니고, C는 초록이 아니다. A의 카드는?",["빨강","파랑","초록","빨강 또는 초록","알 수 없다"],2,"B가 파랑이다. C는 초록이 아니므로 빨강, 따라서 A는 초록이다.","조건 배치"),
      ("모든 승인된 도면은 검토를 마쳤다. 도면 M은 승인을 받았다. 반드시 참인 것은?",["M은 검토를 마쳤다.","검토한 도면은 모두 승인되었다.","M은 현장에 배포되었다.","미승인 도면은 검토되지 않았다.","검토 여부를 알 수 없다."],0,"승인된 도면은 검토를 마쳤다는 규칙에 M을 대입한다.","명제 추리"),
      ("회의 J는 K보다 먼저, L은 K보다 나중이다. 반드시 참인 것은?",["J는 L보다 먼저다.","L은 J보다 먼저다.","K는 J보다 먼저다.","J와 L은 연속한다.","순서를 알 수 없다."],0,"J<K이고 K<L이므로 J<L이다.","순서 추론"),
      ("직무 교육은 월요일부터 수요일 사이 하루에 열린다. A는 화요일이 아니고, B는 A보다 늦다. B가 월요일일 수 있는가?",["가능하다.","불가능하다.","A가 월요일이면 가능하다.","A와 B가 같은 날이면 가능하다.","조건이 모순이다."],1,"B는 A보다 늦어야 하므로 월요일일 수 없다.","시간 조건"),
      ("작업 순서를 정한다. 검사 작업은 포장보다 먼저이고, 포장은 출하보다 먼저다. 반드시 참인 것은?",["검사는 출하보다 먼저다.","출하는 검사보다 먼저다.","포장과 검사는 동시에 한다.","검사는 첫 작업이다.","순서는 정할 수 없다."],0,"검사<포장<출하이므로 검사는 출하보다 앞선다.","조건 연쇄")
    ]
    out=[]
    for i,(q,choices,ans,exp,skill) in enumerate(raw):
        opts,idx=rotate_options(rng,choices,ans)
        out.append(mc(q,opts,idx,exp,"logic",skill,("기초","표준","도전")[i%3],topic="조건 추론"))
    return out


def sequence_items(rng):
    out=[]
    for i in range(10):
        t=i%6
        if t==0:
            a=rng.randrange(2,15); d=rng.randrange(2,9); seq=[a+j*d for j in range(5)]; ans=a+5*d; rule=f"매번 {d}씩 더한다."
        elif t==1:
            a=rng.randrange(1,5); f=rng.choice([2,3]); seq=[a*f**j for j in range(5)]; ans=a*f**5; rule=f"매번 {f}배 한다."
        elif t==2:
            a=rng.randrange(1,5); c=rng.randrange(1,5); seq=[a]
            for _ in range(4): seq.append(seq[-1]*2+c)
            ans=seq[-1]*2+c; rule=f"앞 항에 2를 곱하고 {c}를 더한다."
        elif t==3:
            a=rng.randrange(1,5); off=rng.randrange(0,5); seq=[(a+j)**2+off for j in range(5)]; ans=(a+5)**2+off; rule=f"연속 자연수의 제곱에 {off}을 더한 수다."
        elif t==4:
            a=rng.randrange(1,9); x=rng.randrange(2,7); y=rng.randrange(1,6); seq=[a]
            for j in range(4): seq.append(seq[-1]+(x if j%2==0 else y))
            ans=seq[-1]+x; rule=f"차이가 +{x}, +{y}로 번갈아 나타난다."
        else:
            a=rng.randrange(1,9); seq=[a]
            for j in range(1,5): seq.append(seq[-1]+j*j)
            ans=seq[-1]+25; rule="차이가 1, 4, 9, 16, 25로 이어진다."
        delta=max(1,round(ans*.07)); nums=[ans,ans+delta,max(0,ans-delta),ans+1,ans*2]
        nums=list(dict.fromkeys(nums))
        while len(nums)<5: nums.append(ans+len(nums)+2)
        opts,idx=rotate_options(rng,[str(x) for x in nums[:5]],0)
        out.append(mc(f"다음 수열의 빈칸에 들어갈 수는?\n{', '.join(map(str,seq))}, (   )",opts,idx,f"{rule} 따라서 다음 수는 {ans}다.","seq","수열 규칙 찾기",("기초","표준","도전")[i%3],topic="수열"))
    return out


def generate(seed=20261001, per_area=10):
    rng=random.Random(seed)
    makers={"lang":lang_items,"data":data_items,"math":math_items,"logic":logic_items,"seq":sequence_items}
    out={}
    for area in AREAS:
        items=makers[area](rng)
        if per_area>len(items):
            # Keep question IDs unique by generating another seeded batch.
            extra=makers[area](rng)
            items += extra[:per_area-len(items)]
        out[area]=items[:per_area]
    return out


def main():
    parser=argparse.ArgumentParser(description="sinji용 SKCT 추가 랜덤 문항 생성기")
    parser.add_argument('--count',type=int,default=10,help='영역별 추가 문항 수 (기본 10)')
    parser.add_argument('--seed',type=int,default=20261001,help='재현 가능한 난수 시드')
    parser.add_argument('--output',type=Path,default=OUT,help='출력 경로 (기본 extra.json)')
    args=parser.parse_args()
    if not 1<=args.count<=10:
        parser.error('--count는 영역별 1~10개로 입력하세요. 현재 템플릿의 최대값은 10입니다.')
    try:
        old=json.loads(args.output.read_text(encoding='utf-8'))
        kept={k:v for k,v in old.get('q',{}).items() if not (isinstance(v,dict) and '_meta' in v)}
    except FileNotFoundError:
        kept={}
    fresh=generate(args.seed,args.count)
    next_id=max([int(k) for k in kept if str(k).isdigit()] or [0])+1
    for area in AREAS:
        for item in fresh[area]:
            kept[str(next_id)]=item;next_id+=1
    doc={"title":"추가 문항(직접 작성 + 정보 기반 생성)","q":kept}
    args.output.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"{args.output}: 기존 직접 작성 {sum('_meta' not in q for q in kept.values())}개 + 신규 생성 {sum(len(x) for x in fresh.values())}개")
    print('영역별 신규:', ', '.join(f'{AREA_NAMES[a]} {len(fresh[a])}' for a in AREAS))
    print(f'시드: {args.seed}')

if __name__=='__main__':
    main()
