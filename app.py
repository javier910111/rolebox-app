import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="롤박스 직업 탐색",
    page_icon="👨‍💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #4CAF50, #2196F3);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .job-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .job-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    .completed-job {
        border-color: #4CAF50;
        background: linear-gradient(135deg, #f8fff8, #e8f5e8);
    }
    .points-badge {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem;
    }
    .login-container {
        max-width: 400px;
        margin: 2rem auto;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .skill-tag {
        background: #e3f2fd;
        color: #1976d2;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        border-radius: 15px;
        font-size: 0.85em;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# 데이터 정의
CAREER_PLAN = {
    '3월': {'theme': '우리 원과 친구들', 'jobs': {'5세': '사육사', '6세': '조향사', '7세': '판사'}},
    '4월': {'theme': '봄과 동식물', 'jobs': {'5세': '곤충학자', '6세': '고생물학자', '7세': '스마트파머'}},
    '5월': {'theme': '나와 가족', 'jobs': {'5세': '안경사', '6세': '비타민 연구원', '7세': '약사'}},
    '6월': {'theme': '우리 동네', 'jobs': {'5세': '치과의사', '6세': '주얼리 디자이너', '7세': '외과의사'}},
    '7월': {'theme': '여름과 건강', 'jobs': {'5세': '발레무용가', '6세': '기상캐스터', '7세': '생명공학자'}},
    '8월': {'theme': '교통기관', 'jobs': {'5세': '물리학자', '6세': '승무원', '7세': '자동차 디자이너'}},
    '9월': {'theme': '세계 속의 우리나라', 'jobs': {'5세': '복원 전문가', '6세': '크리에이터', '7세': '한의사'}},
    '10월': {'theme': '가을', 'jobs': {'5세': '컬러리스트', '6세': '건축 공학 기술자', '7세': '패션 디자이너'}},
    '11월': {'theme': '환경과 생활', 'jobs': {'5세': '환경운동가', '6세': '천문학자', '7세': '과학수사대'}},
    '12월': {'theme': '겨울', 'jobs': {'5세': '캐릭터 디자이너', '6세': '소방관', '7세': '사회복지사'}},
    '1월': {'theme': '생활도구', 'jobs': {'5세': '헤어 디자이너', '6세': '목수', '7세': '로봇공학자'}},
    '2월': {'theme': '형님반에 가요', 'jobs': {'5세': '경찰관', '6세': '산부인과의사', '7세': '도시설계사'}}
}

JOB_DESCRIPTIONS = {
    '사육사': {
        'description': '동물들을 돌보고 건강하게 키우는 일을 해요 🐾',
        'activities': ['동물에게 먹이 주기', '우리 청소하기', '건강 체크하기', '관람객 안내하기'],
        'skills': ['관찰력', '책임감', '동물 사랑', '체력'],
        'emoji': '🐘',
        'fun_fact': '동물원 사육사는 하루에 30종 이상의 동물을 돌봐요!'
    },
    '곤충학자': {
        'description': '곤충을 연구하고 새로운 사실을 발견해요 🔬',
        'activities': ['곤충 채집하기', '현미경으로 관찰하기', '생태 연구하기', '논문 작성하기'],
        'skills': ['탐구력', '인내심', '세심함', '기록력'],
        'emoji': '🦋',
        'fun_fact': '지구에는 100만 종 이상의 곤충이 살고 있어요!'
    },
    '조향사': {
        'description': '좋은 향수와 향을 만드는 전문가예요 🌸',
        'activities': ['향 재료 섞기', '새로운 향 개발하기', '향수 테스트하기', '고객 상담하기'],
        'skills': ['후각', '창의력', '집중력', '감성'],
        'emoji': '🌺',
        'fun_fact': '조향사는 3000가지 이상의 향을 구별할 수 있어요!'
    },
    '판사': {
        'description': '공정하게 판결을 내리는 법의 수호자예요 ⚖️',
        'activities': ['사건 검토하기', '재판 진행하기', '공정한 판결하기', '법률 연구하기'],
        'skills': ['판단력', '공정성', '논리력', '책임감'],
        'emoji': '⚖️',
        'fun_fact': '판사가 되려면 사법고시에 합격해야 해요!'
    },
    '고생물학자': {
        'description': '화석을 연구해서 고대 생물을 알아내요 🦕',
        'activities': ['화석 발굴하기', '화석 분석하기', '고대 생물 복원하기', '연구 발표하기'],
        'skills': ['탐구력', '상상력', '인내심', '분석력'],
        'emoji': '🦕',
        'fun_fact': '공룡 화석은 6500만 년 전 것들이에요!'
    },
    '비타민 연구원': {
        'description': '건강에 좋은 비타민을 연구해요 💊',
        'activities': ['비타민 성분 분석하기', '실험하기', '건강 효과 연구하기', '제품 개발하기'],
        'skills': ['분석력', '꼼꼼함', '과학적 사고', '집중력'],
        'emoji': '💊',
        'fun_fact': '비타민 C는 괴혈병을 예방해줘요!'
    }
}

# 세션 스테이트 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_points' not in st.session_state:
    st.session_state.user_points = 150
if 'completed_jobs' not in st.session_state:
    st.session_state.completed_jobs = []
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'selected_month' not in st.session_state:
    st.session_state.selected_month = None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    # 데모용 계정들
    demo_users = {
        'demo': hash_password('rolebox2024'),
        'test_kindergarten': hash_password('test123'),
        'sample_daycare': hash_password('sample123'),
        '행복어린이집': hash_password('happy123'),
        '무지개유치원': hash_password('rainbow123')
    }
    return username in demo_users and demo_users[username] == hash_password(password)

def login_page():
    st.markdown('<div class="main-header"><h1>🎭 롤박스 직업 탐색</h1><p>직업 체험 놀이 교육 플랫폼</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("### 🔐 기관 로그인")
        
        with st.form("login_form"):
            username = st.text_input("기관 아이디", placeholder="기관 아이디를 입력하세요")
            password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
            submitted = st.form_submit_button("🚀 로그인", use_container_width=True)
            
            if submitted:
                if authenticate(username, password):
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.success("로그인 성공! 🎉")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ 아이디 또는 비밀번호가 잘못되었습니다.")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.info("""
        **🧪 데모 계정들**  
        - `demo` / `rolebox2024`  
        - `test_kindergarten` / `test123`  
        - `행복어린이집` / `happy123`  
        - `무지개유치원` / `rainbow123`
        """)

def main_app():
    # 헤더
    col1, col2, col3 = st.columns([4, 2, 1])
    with col1:
        st.markdown('<div class="main-header"><h1>🎭 롤박스 직업 탐색</h1><p>36개 직업으로 떠나는 모험!</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="points-badge">⭐ {st.session_state.user_points} 포인트</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="points-badge">🏆 {len(st.session_state.completed_jobs)}/12 완료</div>', unsafe_allow_html=True)
    with col3:
        if st.button("🚪 로그아웃", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()
    
    st.markdown("---")
    
    # 연령 선택
    st.markdown("### 👶 연령을 선택하세요")
    age = st.selectbox("", ["5세", "6세", "7세"], index=0, key="age_select")
    
    # 진행률 표시
    progress = len(st.session_state.completed_jobs) / 12
    st.markdown("### 📊 나의 직업 탐험 여정")
    st.progress(progress, text=f"진행률: {int(progress * 100)}%")
    
    if len(st.session_state.completed_jobs) >= 6:
        st.success("🌟 절반 이상 완료! 정말 대단해요!")
    elif len(st.session_state.completed_jobs) >= 3:
        st.info("💪 좋은 시작이에요! 계속 화이팅!")
    
    st.markdown("---")
    
    # 월별 직업 탐색
    st.markdown("### 📅 월별 직업을 탐험해보세요!")
    
    # 4개씩 나누어서 표시
    months = list(CAREER_PLAN.keys())
    for i in range(0, len(months), 4):
        cols = st.columns(4)
        for j, month in enumerate(months[i:i+4]):
            if j < len(cols):
                with cols[j]:
                    job_name = CAREER_PLAN[month]['jobs'][age]
                    theme = CAREER_PLAN[month]['theme']
                    is_completed = job_name in st.session_state.completed_jobs
                    
                    # 직업 정보 가져오기
                    job_info = JOB_DESCRIPTIONS.get(job_name, {'emoji': '💼', 'description': '흥미진진한 직업이에요!'})
                    emoji = job_info['emoji']
                    
                    # 직업 카드
                    card_class = "completed-job" if is_completed else "job-card"
                    
                    st.markdown(f"""
                    <div class="{card_class}">
                        <h3 style="text-align: center; margin-bottom: 1rem;">{emoji}</h3>
                        <h4 style="color: #333; margin-bottom: 0.5rem;">{month}</h4>
                        <p style="font-weight: bold; color: #2196F3; margin-bottom: 0.5rem;">{job_name}</p>
                        <p style="color: #666; font-size: 0.85em; margin-bottom: 1rem;">{theme}</p>
                        {'<p style="color: #4CAF50; font-weight: bold;">✅ 체험 완료!</p>' if is_completed else '<p style="color: #FF9800;">🎯 체험 대기</p>'}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"🔍 {month} 자세히 보기", key=f"detail_{month}", use_container_width=True):
                        st.session_state.selected_month = month
    
    # 선택된 직업 상세 정보
    if st.session_state.selected_month:
        month = st.session_state.selected_month
        job_name = CAREER_PLAN[month]['jobs'][age]
        
        st.markdown("---")
        st.markdown(f"## 🔍 {month} - {job_name}")
        
        if job_name in JOB_DESCRIPTIONS:
            job_info = JOB_DESCRIPTIONS[job_name]
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {job_info['emoji']} {job_name}")
                st.write(job_info['description'])
                if 'fun_fact' in job_info:
                    st.info(f"💡 **재미있는 사실**: {job_info['fun_fact']}")
            
            with col2:
                if job_name not in st.session_state.completed_jobs:
                    if st.button("✨ 체험 완료하기", type="primary", use_container_width=True):
                        st.session_state.completed_jobs.append(job_name)
                        st.session_state.user_points += 50
                        st.success("🎉 체험 완료! +50포인트!")
                        st.balloons()
                        st.rerun()
                else:
                    st.success("✅ 완료됨!")
                    st.write(f"획득한 포인트: +50P")
            
            # 상세 정보
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎯 주요 활동")
                for i, activity in enumerate(job_info['activities'], 1):
                    st.write(f"{i}. {activity}")
            
            with col2:
                st.markdown("#### 💪 필요한 능력")
                skills_html = " ".join([f'<span class="skill-tag">{skill}</span>' for skill in job_info['skills']])
                st.markdown(skills_html, unsafe_allow_html=True)

# 메인 로직
if not st.session_state.logged_in:
    login_page()
else:
    main_app()

# 사이드바 정보
with st.sidebar:
    if st.session_state.logged_in:
        st.markdown("### 📊 내 정보")
        st.write(f"**기관명**: {st.session_state.current_user}")
        st.write(f"**완료 직업**: {len(st.session_state.completed_jobs)}개")
        st.write(f"**포인트**: {st.session_state.user_points}P")
        
        if st.session_state.completed_jobs:
            st.markdown("#### 🏆 완료한 직업들")
            for job in st.session_state.completed_jobs:
                job_emoji = JOB_DESCRIPTIONS.get(job, {}).get('emoji', '💼')
                st.write(f"{job_emoji} {job}")
        
        st.markdown("---")
        st.markdown("### 🎮 미니 게임")
        if st.button("🎲 랜덤 직업 추천"):
            import random
            random_job = random.choice(list(JOB_DESCRIPTIONS.keys()))
            st.success(f"추천 직업: {JOB_DESCRIPTIONS[random_job]['emoji']} {random_job}")
        
        st.markdown("---")
        st.markdown("### 📱 앱 정보")
        st.info("""
        **롤박스 직업 탐색 v2.0**
        
        🎯 36개 직업 체험  
        🏆 포인트 시스템  
        📈 진행률 추적  
        👨‍👩‍👧‍👦 연령별 맞춤 컨텐츠  
        🎮 재미있는 기능들
        """)
    else:
        st.markdown("### 👋 환영합니다!")
        st.write("로그인 후 이용하세요.")