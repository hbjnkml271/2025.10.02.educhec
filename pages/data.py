# Streamlit 앱: 사각형 판단 문제 생성 및 정답 확인
import streamlit as st

# 사각형 종류 및 특징 (연꼴 제거)
quadrilaterals = {
	"일반 사각형": ["네 변이 있다"],
	"평행사변형": ["두 쌍의 대변이 평행하다", "대각선이 서로를 이등분한다"],
	"직사각형": ["네 각이 모두 직각이다", "대각선의 길이가 같다"],
	"마름모": ["네 변의 길이가 같다", "대각선이 서로를 수직이등분한다"],
	"정사각형": ["네 각이 모두 직각이다", "네 변의 길이가 같다", "대각선의 길이가 같다", "대각선이 서로를 수직이등분한다"],
	"사다리꼴": ["한 쌍의 대변만 평행하다"],
	"등변사다리꼴": ["한 쌍의 대변만 평행하다", "다른 두 변의 길이가 같다", "대각선의 길이가 같다"]
}



# 명제(특징)만 제시하는 문제 리스트 생성
example_questions = []
for name, features in quadrilaterals.items():
	example_questions.append({
		"name": name,
		"features": features
	})

# 모든 사각형 포함관계 맵 (더 특수한 사각형이 안쪽)
include_map = {
	"평행사변형": ["직사각형", "마름모", "정사각형"],
	"직사각형": ["정사각형"],
	"마름모": ["정사각형"],
	"사다리꼴": ["등변사다리꼴"],
	"일반 사각형": ["평행사변형", "직사각형", "마름모", "정사각형", "사다리꼴", "등변사다리꼴"],
	"등변사다리꼴": [],
	"정사각형": [],
}

st.title("사각형 판단 문제 (중2 2학기 22개정)")

# 체크박스로 출제할 사각형 선택
selected_types = st.multiselect(
	"문제로 출제할 사각형 종류를 선택하세요:",
	list(quadrilaterals.keys()),
	default=["직사각형", "평행사변형", "마름모", "정사각형", "사다리꼴", "등변사다리꼴"]
)

import random

# 세션 상태로 문제 진행 관리

# 문제 초기화
if 'questions' not in st.session_state or st.session_state.get('reset', False):
	st.session_state['questions'] = random.sample([q for q in example_questions if q["name"] in selected_types], k=min(10, len(selected_types)))
	st.session_state['current'] = 0
	st.session_state['answers'] = []
	st.session_state['reset'] = False

questions = st.session_state['questions']
current = st.session_state['current']
def get_score(answers, questions):
	# 맞은 개수: 완전 정답(정답만 입력, 포함관계 아님)만 인정
	cnt = 0
	for idx, ans in enumerate(answers):
		correct_name = questions[idx]["name"]
		user_raw = ans["user"]
		user_vals = [v.strip() for v in user_raw.replace('/',',').replace(' ',',').split(',') if v.strip()]
		# 포함관계에서 더 특수한(안쪽) 사각형이 하나라도 입력된 경우 주황색 안내
		inner = [v for v in user_vals if v in include_map.get(correct_name, [])]
		if correct_name in user_vals and len(user_vals) == 1 and not inner:
			cnt += 1
	return cnt

answers = st.session_state['answers']
score = get_score(answers, questions)
answers = st.session_state['answers']


if questions:
	question = questions[current]
	st.markdown(f"### 문제 {current+1} / {len(questions)}")
	st.write(f"다음 명제(특징)를 가진 사각형의 이름을 쓰세요:")
	st.write(", ".join(question["features"]))


	# 답안 입력창/버튼 활성화 상태 관리
	answered = current < len(answers)
	check_disabled = answered
	next_disabled = not answered or (current == len(answers))

	if answered:
		prev_answer = answers[current]["user"]
		user_answer = st.text_input("이 사각형의 이름을 입력하세요:", value=prev_answer, key=f"answer_{current}", disabled=True)
	else:
		user_answer = st.text_input("이 사각형의 이름을 입력하세요:", key=f"answer_{current}")

	col1, col2 = st.columns([1,1])
	check_clicked = col1.button("정답 확인", key=f"check_{current}", disabled=check_disabled)
	# 정답확인 버튼을 누르면 다음문제 버튼 즉시 활성화
	if answered or check_clicked:
		next_disabled = False
	next_clicked = col2.button("다음문제", key=f"next_{current}", disabled=next_disabled)

	# 정답 여부를 명확히 표시 (여러 답안 처리)
	if answered or check_clicked:
		if answered:
			user_raw = answers[current]["user"]
		else:
			user_raw = user_answer.strip()
		# 답안 분리: 쉼표, /, 띄어쓰기 기준
		user_vals = [v.strip() for v in user_raw.replace('/',',').replace(' ',',').split(',') if v.strip()]
		correct_name = question["name"]

		# 포함관계 역방향(정답과 포함관계 답을 동시에 입력하면 오답)
		def is_wrong_include(correct, vals):
			# 정답과 포함관계 답이 동시에 있으면 오답
			for inc in include_map.get(correct, []):
				if correct in vals and inc in vals:
					return True
			return False

		# 정답 포함 여부
		is_correct = correct_name in user_vals
		# 포함관계 성립 여부: 정답 없이 더 특수한 답만 입력
		include_correct = False
		for inc in include_map.get(correct_name, []):
			if inc in user_vals and correct_name not in user_vals:
				include_correct = True
		# 포함관계에서 더 특수한(안쪽) 사각형이 하나만 입력된 경우에도 주황색 안내
		inner = [v for v in user_vals if v in include_map.get(correct_name, [])]

		# 완전 정답: 정답만 입력
		if is_correct and len(user_vals) == 1 and not inner:
			st.success("정답입니다!")
		# 포함관계에서 더 특수한(안쪽) 사각형이 하나만 입력된 경우에도 주황색 안내
		elif is_correct and len(user_vals) == 1 and inner:
			user_features = [quadrilaterals.get(v, None) for v in user_vals]
			user_comment = f"입력한 답: {', '.join(user_vals)}\n각 답의 특징: " + ", ".join([', '.join(f) if f else '알 수 없음' for f in user_features])
			answer_comment = f"정답: '{correct_name}'\n'{', '.join(inner)}'은(는) '{correct_name}'의 성질을 모두 만족합니다. 하지만 명확한 답은 '{correct_name}'이므로 다시 생각해보세요!\n이 사각형이 정답인 이유: {', '.join(question['features'])}"
			st.markdown(f"<span style='color:orange'><b>포함관계가 성립하는 답입니다. 다시 생각해보세요!</b><br>{user_comment}<br><br>{answer_comment}</span>", unsafe_allow_html=True)
		# 정답 포함, 다른 답도 입력
		elif is_correct:
			# 포함관계에서 더 특수한(안쪽) 사각형이 함께 입력된 경우 주황색 안내
			inner = [v for v in user_vals if v in include_map.get(correct_name, [])]
			user_features = [quadrilaterals.get(v, None) for v in user_vals]
			user_comment = f"입력한 답: {', '.join(user_vals)}\n각 답의 특징: " + ", ".join([', '.join(f) if f else '알 수 없음' for f in user_features])
			answer_comment = f"정답: '{correct_name}'\n이 사각형이 정답인 이유: {', '.join(question['features'])}"
			if inner:
				st.markdown(f"<span style='color:orange'><b>포함관계가 성립하는 답입니다. 다시 생각해보세요!</b><br>{user_comment}<br><br>{answer_comment}</span>", unsafe_allow_html=True)
			else:
				st.markdown(f"<span style='color:red'><b>오답입니다.</b><br>{user_comment}<br><br>{answer_comment}</span>", unsafe_allow_html=True)
		# 포함관계가 성립하는 답을 적었을 때(정답 없이 더 특수한 답만 입력)
		elif include_correct:
			user_features = [quadrilaterals.get(v, None) for v in user_vals]
			user_comment = f"입력한 답: {', '.join(user_vals)}\n각 답의 특징: " + ", ".join([', '.join(f) if f else '알 수 없음' for f in user_features])
			answer_comment = f"정답: '{correct_name}'\n'{', '.join([v for v in user_vals if v != correct_name])}'은(는) '{correct_name}'의 성질을 모두 만족합니다. 하지만 명확한 답은 '{correct_name}'이므로 다시 생각해보세요!\n이 사각형이 정답인 이유: {', '.join(question['features'])}"
			st.markdown(f"<span style='color:orange'><b>포함관계가 성립하는 답입니다. 다시 생각해보세요!</b><br>{user_comment}<br><br>{answer_comment}</span>", unsafe_allow_html=True)
		# 포함관계가 옳지 않을 때(정사각형 명제에 직사각형, 정사각형 같이 입력 등)
		elif is_wrong_include(correct_name, user_vals):
			user_features = [quadrilaterals.get(v, None) for v in user_vals]
			user_comment = f"입력한 답: {', '.join(user_vals)}\n각 답의 특징: " + ", ".join([', '.join(f) if f else '알 수 없음' for f in user_features])
			answer_comment = f"정답: '{correct_name}'\n정답과 포함관계가 성립하는 답을 동시에 입력하면 오답입니다.\n이 사각형이 정답인 이유: {', '.join(question['features'])}"
			st.markdown(f"<span style='color:red'><b>오답입니다.</b><br>{user_comment}<br><br>{answer_comment}</span>", unsafe_allow_html=True)
		# 부분 정답: 정답 포함, 다른 답도 입력
		elif is_correct:
			user_features = [quadrilaterals.get(v, None) for v in user_vals]
			user_comment = f"입력한 답: {', '.join(user_vals)}\n각 답의 특징: " + ", ".join([', '.join(f) if f else '알 수 없음' for f in user_features])
			answer_comment = f"정답: '{correct_name}'\n정답과 다른 답을 동시에 입력하면 오답입니다.\n이 사각형이 정답인 이유: {', '.join(question['features'])}"
			st.markdown(f"<span style='color:red'><b>오답입니다.</b><br>{user_comment}<br><br>{answer_comment}</span>", unsafe_allow_html=True)
		# 오답
		else:
			user_features = [quadrilaterals.get(v, None) for v in user_vals]
			user_comment = f"입력한 답: {', '.join(user_vals)}\n각 답의 특징: " + ", ".join([', '.join(f) if f else '알 수 없음' for f in user_features])
			answer_comment = f"정답: '{correct_name}'\n이 사각형이 정답인 이유: {', '.join(question['features'])}"
			st.markdown(f"<span style='color:red'><b>오답입니다.</b><br>{user_comment}<br><br>{answer_comment}</span>", unsafe_allow_html=True)

	# 정답 확인 버튼 클릭 시
	if check_clicked and not answered:
		answers.append({
			"user": user_answer.strip(),
			"question": question["name"]
		})
		st.session_state['answers'] = answers


	# 이미 답을 제출한 경우 정답 여부 표시는 위 코멘트 로직에서만 판단

	# 다음문제 버튼 클릭 시
	if next_clicked and answered and current < len(questions)-1:
		st.session_state['current'] += 1
		st.rerun()

	# 마지막 문제까지 모두 답했을 때 결과 표시 및 다시 하기 버튼
	if current == len(questions)-1 and len(answers) == len(questions):
		st.markdown(f"## 결과: {score} / {len(questions)} 문제 정답!")
		st.write("각 문제별 답안:")
		for idx, ans in enumerate(answers):
			user_raw = ans["user"]
			user_vals = [v.strip() for v in user_raw.replace('/',',').replace(' ',',').split(',') if v.strip()]
			correct_name = questions[idx]["name"]
			# 포함관계에서 더 특수한(안쪽) 사각형이 하나만 입력된 경우에도 주황색 안내
			inner_map = {
				"평행사변형": ["직사각형", "마름모", "정사각형"],
				"직사각형": ["정사각형"],
				"마름모": ["정사각형"],
				"사다리꼴": ["등변사다리꼴"],
			}
			inner = [v for v in user_vals if v in inner_map.get(correct_name, [])]
			if correct_name in user_vals and len(user_vals) == 1 and not inner:
				result = 'O'
			else:
				result = 'X'
			st.write(f"{idx+1}번 문제: 입력='{ans['user']}', 정답='{ans['question']}', {result}")
		if st.button("다시 하기"):
			st.session_state['reset'] = True
			st.rerun()
else:
	st.info("선택한 사각형 종류가 없습니다. 체크박스에서 문제로 출제할 사각형을 선택하세요.")

