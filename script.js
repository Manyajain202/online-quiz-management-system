const $ = (id) => document.getElementById(id);

async function api(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: { "Content-Type": "application/json", ...(options.headers || {}) }
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || data.message || "Request failed");
    return data;
}

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[c]));
}

async function logout() {
    await api("/api/logout", {method:"POST"});
    location.href = "/";
}

async function setupRegister() {
    const form = $("registerForm");
    if (!form) return;
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const password = $("password").value;
        const confirm = $("confirmPassword").value;
        const msg = $("authMessage");
        if (password !== confirm) { msg.textContent = "Passwords do not match."; msg.className="message error"; return; }
        try {
            await api("/api/register", {method:"POST", body:JSON.stringify({name:$("name").value,email:$("email").value,password})});
            msg.textContent = "Registration successful! Redirecting to login...";
            msg.className = "message success";
            setTimeout(() => location.href="/login", 600);
        } catch (err) { msg.textContent=err.message; msg.className="message error"; }
    });
}

async function setupLogin() {
    const form = $("loginForm");
    if (!form) return;
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const msg = $("authMessage");
        try {
            const data = await api("/api/login", {method:"POST", body:JSON.stringify({email:$("email").value,password:$("password").value})});
            const selectedRole = $("role").value;
            if (selectedRole && selectedRole !== data.role) throw new Error(`This account is a ${data.role} account.`);
            location.href = data.role === "admin" ? "/admin-dashboard" : "/student-dashboard";
        } catch (err) { msg.textContent=err.message; msg.className="message error"; }
    });
}

async function loadStudentDashboard() {
    if (!$("quizGrid")) return;
    const me = await api("/api/me");
    if (!me.logged_in) { location.href="/login"; return; }
    $("welcomeTitle").textContent = `Welcome, ${me.name}!`;
    const quizzes = await api("/api/quizzes");
    const results = await api("/api/results");
    $("availableCount").textContent = quizzes.length;
    $("completedCount").textContent = results.length;
    const avg = results.length ? Math.round(results.reduce((a,r)=>a+Number(r.percentage),0)/results.length) : 0;
    $("averageScore").textContent = avg + "%";
    $("quizGrid").innerHTML = quizzes.map(q => `<div class="quiz-card"><div class="quiz-icon">📝</div><h3>${escapeHtml(q.title)}</h3><p>${escapeHtml(q.description)}</p><div class="quiz-info"><span>${q.duration} min</span><span>Timed</span></div><a href="/quiz?id=${q.id}" class="dashboard-btn">Start Quiz</a></div>`).join("");
    $("recentResults").innerHTML = results.length ? results.slice(0,5).map(r=>`<div class="result-card"><div><h3>${escapeHtml(r.title)}</h3><p>Score: ${r.score} / ${r.total}</p></div><strong>${Number(r.percentage).toFixed(0)}%</strong></div>`).join("") : `<div class="empty-state">No attempts yet. Take your first quiz!</div>`;
}

let quizData=null, currentQuestion=0, score=0, timerInterval=null, timeLeft=0, totalTime=0;

async function loadQuizPage() {
    if (!$("questionText")) return;
    const me = await api("/api/me");
    if (!me.logged_in) { location.href="/login"; return; }
    const id = new URLSearchParams(location.search).get("id") || "1";
    quizData = await api(`/api/quizzes/${id}`);
    $("quizTitle").textContent=quizData.quiz.title;
    $("quizDescription").textContent=quizData.quiz.description;
    $("questionTotal").textContent=quizData.questions.length;
    timeLeft = quizData.quiz.duration * 60;
    totalTime = timeLeft;
    currentQuestion=0; score=0;
    if ($("liveScore")) $("liveScore").textContent = "Score: 0";
    renderQuestion();
    startTimer();
    $("nextButton").onclick = nextQuestion;
}

function renderQuestion() {
    const q=quizData.questions[currentQuestion];
    $("questionNumber").textContent=currentQuestion+1;
    $("questionText").textContent=q.question;
    $("optionA").textContent="A. "+q.option_a;
    $("optionB").textContent="B. "+q.option_b;
    $("optionC").textContent="C. "+q.option_c;
    $("optionD").textContent="D. "+q.option_d;
    $("progressFill").style.width=((currentQuestion+1)/quizData.questions.length*100)+"%";
    document.querySelectorAll('input[name="answer"]').forEach(x=>x.checked=false);
    $("nextButton").textContent=currentQuestion===quizData.questions.length-1?"Submit Quiz":"Next Question";
}

function startTimer() {
    clearInterval(timerInterval);
    updateTimer();
    timerInterval=setInterval(()=>{
        timeLeft--; updateTimer();
        if(timeLeft<=0){ clearInterval(timerInterval); finishQuiz(true); }
    },1000);
}
function updateTimer(){ const m=Math.floor(timeLeft/60),s=timeLeft%60; $("timer").textContent=`${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`; if ($("timeRemaining")) $("timeRemaining").textContent=`Time Left: ${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`; }

function nextQuestion(){
    const selected=document.querySelector('input[name="answer"]:checked');
    if(!selected){ $("quizMessage").textContent="Please select an answer."; $("quizMessage").className="message error"; return; }
    if(selected.value===quizData.questions[currentQuestion].answer) score++;
    if ($("liveScore")) $("liveScore").textContent = `Score: ${score}`;
    if(currentQuestion<quizData.questions.length-1){ currentQuestion++; $("quizMessage").textContent=""; renderQuestion(); }
    else finishQuiz(false);
}

async function finishQuiz(timeUp){
    clearInterval(timerInterval);
    const timeTaken = totalTime - Math.max(timeLeft, 0);
    try{
        await api("/api/results",{method:"POST",body:JSON.stringify({quiz_id:quizData.quiz.id,score,total:quizData.questions.length})});
        location.href=`/result?score=${score}&total=${quizData.questions.length}&quiz=${quizData.quiz.id}&time=${timeTaken}&timeup=${timeUp ? 1 : 0}`;
    }catch(err){ $("quizMessage").textContent=err.message; $("quizMessage").className="message error"; }
}

async function loadResultPage(){
    if(!$("percentage")) return;
    const p=new URLSearchParams(location.search); const scoreVal=Number(p.get("score")||0); const total=Number(p.get("total")||0);
    const percentage=total?Math.round(scoreVal/total*100):0;
    const seconds=Math.max(0, Number(p.get("time")||0));
    const tm=Math.floor(seconds/60), ts=seconds%60;
    $("score").textContent=scoreVal; $("total").textContent=total; $("percentage").textContent=percentage+"%";
    if ($("timeTaken")) $("timeTaken").textContent=`${String(tm).padStart(2,"0")}:${String(ts).padStart(2,"0")}`;
    $("resultMessage").textContent=percentage>=80?"Excellent work! Keep it up!":percentage>=60?"Good job! Keep practicing!":percentage>=40?"Nice effort! You can improve with more practice.":"Keep practicing and try again!";
    if(p.get("quiz")) $("retakeLink").href=`/quiz?id=${p.get("quiz")}`;
}

async function loadAdmin(){
    if(!$("adminQuizList")) return;
    const me=await api("/api/me"); if(!me.logged_in || me.role!=="admin"){location.href="/login";return;}
    const quizzes=await api("/api/quizzes"); const results=await api("/api/results");
    $("adminQuizCount").textContent=quizzes.length; $("adminResultCount").textContent=results.length;
    const avg=results.length?Math.round(results.reduce((a,r)=>a+Number(r.percentage),0)/results.length):0; $("adminAverage").textContent=avg+"%";
    $("adminQuizList").innerHTML=quizzes.map(q=>`<div class="admin-row"><div><b>${escapeHtml(q.title)}</b><small>${escapeHtml(q.description)} · ${q.duration} min</small></div><a href="/quiz?id=${q.id}" class="table-btn">Preview</a></div>`).join("");
    $("adminResults").innerHTML=results.length?results.map(r=>`<tr><td>${escapeHtml(r.name)}</td><td>${escapeHtml(r.title)}</td><td>${r.score} / ${r.total}</td><td>${Number(r.percentage).toFixed(0)}%</td></tr>`).join(""):`<tr><td colspan="4">No student results yet.</td></tr>`;
}

function setupCreateQuiz(){
    const form=$("createQuizForm"); if(!form) return;
    $("addQuestion").onclick=()=>{
        const count=document.querySelectorAll(".question-form").length+1; const wrap=document.createElement("div"); wrap.className="quiz-form-card question-form";
        wrap.innerHTML=`<h2>Question ${count}</h2><div class="form-group"><label>Question</label><textarea class="question" rows="2" required></textarea></div><div class="form-group"><label>Option A</label><input class="optionA" required></div><div class="form-group"><label>Option B</label><input class="optionB" required></div><div class="form-group"><label>Option C</label><input class="optionC" required></div><div class="form-group"><label>Option D</label><input class="optionD" required></div><div class="form-group"><label>Correct Answer</label><select class="correctAnswer"><option>A</option><option>B</option><option>C</option><option>D</option></select></div>`;
        $("questionForms").appendChild(wrap);
    };
    form.onsubmit=async e=>{e.preventDefault(); try{const questions=[...document.querySelectorAll(".question-form")].map(c=>({question:c.querySelector(".question").value,option_a:c.querySelector(".optionA").value,option_b:c.querySelector(".optionB").value,option_c:c.querySelector(".optionC").value,option_d:c.querySelector(".optionD").value,answer:c.querySelector(".correctAnswer").value})); await api("/api/quizzes",{method:"POST",body:JSON.stringify({title:$("quizTitle").value,description:$("quizDescription").value,duration:$("duration").value,questions})}); $("createMessage").textContent="Quiz created successfully!"; $("createMessage").className="message success"; setTimeout(()=>location.href="/admin-dashboard",700);}catch(err){$("createMessage").textContent=err.message;$("createMessage").className="message error";}};
}

document.addEventListener("DOMContentLoaded",()=>{
    setupRegister(); setupLogin(); loadStudentDashboard(); loadQuizPage(); loadResultPage(); loadAdmin(); setupCreateQuiz();
});
