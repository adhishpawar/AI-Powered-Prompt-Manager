# 🧠 AI-Powered-Prompt-Manager (Django + OpenAI)

A Django-based REST API that transforms vague user intents into **clear, precise, and AI-ready prompts**.  
The system leverages **OpenAI GPT models** to:
1. Expand vague intents into richer, context-aware descriptions.
2. Generate structured prompts ready for direct AI consumption.
3. Provide feedback, clarity scoring, and categorization for continuous improvement.

---

## 🚀 Features

- **User Authentication** – JWT-based auth to protect API endpoints.
- **Context-Enriched Prompting** – Uses a two-step GPT call:
  1. **Expand vague intent** with GPT before prompt creation.
  2. **Generate a refined, structured prompt** from enriched input.
- **Clarification Chat** – Persistent conversation to refine unclear prompts.
- **Prompt Analysis** – AI-generated feedback, clarity score, and categorization.
- **Semantic Search** – (Optional) Store embeddings in FAISS/Chroma for natural language search.
- **Fully RESTful API** – Built with Django REST Framework.

---

## 📂 Project Structure

```
.
├── prompts/                 # App for prompt handling
│   ├── models.py            # PromptIntent & PromptTemplate models
│   ├── views.py             # Core API logic
│   ├── serializers.py       # DRF serializers
│   ├── urls.py               # API routes
│
├── core/                    # Django project settings
│   ├── settings.py
│   ├── urls.py
│
├── manage.py
├── README.md
└── requirements.txt
```

---

## ⚙️ Tech Stack

- **Backend:** Django 5.x, Django REST Framework
- **AI:** OpenAI GPT-4o / GPT-4o-mini
- **Database:** PostgreSQL (recommended) or SQLite
- **Search (Optional):** FAISS or Chroma for embeddings
- **Auth:** JWT via `djangorestframework-simplejwt`

---

## 🛠 Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/adhishpawar/AI-Powered-Prompt-Manager.git
cd ai-prompt-generator
```

### 2️⃣ Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate    # Mac/Linux
venv\Scripts\activate       # Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set environment variables
Create a `.env` file:
```env
SECRET_KEY=your_django_secret
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/promptdb
OPENAI_API_KEY=sk-xxxxxx
```

### 5️⃣ Apply migrations
```bash
python manage.py migrate
```

### 6️⃣ Run the development server
```bash
python manage.py runserver
```

---

## 🔑 API Endpoints

### **POST** `/api/prompts/generate/`
Generate a structured prompt from user intent.

**Request Body:**
```json
{
  "intent": "I want to write a blog",
  "attributes": {
    "tone": "motivational",
    "target_audience": "young adults"
  }
}
```

**Process:**
1. **Expand intent** (Step 1 – `expand_intent()`).
2. **Build structured prompt** (`build_structured_prompt()`).
3. **Generate refined AI-ready prompt** via GPT.
4. **Analyze** prompt for clarity, category, and feedback.

**Response:**
```json
{
  "template_id": 12,
  "prompt": "Write a motivational blog post targeting young adults about achieving fitness goals.",
  "clarity_score": 9.5,
  "ai_feedback": "Very clear and direct.",
  "status": "success"
}
```

---

## 📌 Core Workflow

1. **User submits intent** via API.
2. **Intent expansion** – GPT rephrases vague idea into detailed context.
3. **Prompt generation** – Another GPT call creates a final, structured prompt.
4. **AI feedback & scoring** – Final prompt analyzed for clarity and relevance.
5. **Storage** – Prompt and metadata stored in DB for search & reuse.

---

## 📊 Future Enhancements
- [ ] Integrate FAISS/Chroma for **semantic search**.
- [ ] Add **versioning** for prompt templates.
- [ ] Build **frontend UI** for managing prompts.
- [ ] Allow **prompt categories** & user tagging.

---

## 🧑‍💻 Development Notes
- Use **environment variables** for all sensitive keys.
- GPT **temperature** can be tuned per use case:
  - **Low (0–0.5):** For precise outputs.
  - **High (1.5–2):** For creative outputs.
- The **clarification_chat** field can store back-and-forth conversation history for deeper refinement.

---

## 📜 License
MIT License — free to use and modify.
