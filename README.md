# Dr. Gupt - AI-Powered Sexual Health Assistant for Rural India  

![Project Banner](assets/banner.png) *(Replace with your image path)*  

## 🌟 Overview  
Dr. Gupt is a **privacy-first AI assistant** that provides **anonymous, judgment-free sexual health guidance** in Hindi via phone calls. Designed for rural India, it combats stigma and connects users to certified practitioners.  

---

## 🚀 Key Features  

### 🔒 For Users  
- **100% Anonymous** consultations via phone calls  
- **Hindi-language** AI with local dialect understanding  
- **Immediate basic diagnosis** for common conditions  
- **Nearest clinic referrals** with discreet booking  
- **No smartphones needed** – works on basic feature phones  

### ⚙️ Technical Stack  
| Component          | Technology Used          |  
|--------------------|--------------------------|  
| Voice Interface    | Exotel Telephony         |  
| Speech-to-Text     | Sarvam AI STT            |  
| AI Brain           | Sarvam Chat Completion   |  
| Text-to-Speech     | Sarvam TTS               |  
| Appointments       | Practo API Integration   |  

---

## 📞 How It Works  

### User Flow  
1. **Call** → Dials toll-free number  
2. **Describe** → Speaks naturally (e.g., _"Mujhe na, vo hai..."_)  
3. **Get Help** → Receives:  
   - Basic diagnosis  
   - Self-care tips  
   - Clinic referrals *(optional)*  
4. **Book** → Discreet appointment via WhatsApp/SMS  

### System Flow  
graph TD
    A[User Call] --> B(Exotel)
    B --> C[Sarvam STT]
    C --> D[AI Diagnosis]
    D --> E[Sarvam TTS]
    E --> F[User Response]
    D --> G[Clinic Lookup Tool]
    G --> H[Practo Booking]



🛠️ Setup & Deployment
Prerequisites
Sarvam API keys (sk_ot81c8fq_...)

Exotel account

Practo developer access


Installation
bash
git clone https://github.com/yourusername/dr-gupt
cd dr-gupt
echo "SARVAM_KEY=your_key" > .env
pip install -r requirements.txt
Environment Variables
ini
EXOTEL_SID=your_exotel_sid
PRACTO_TOKEN=your_practo_token
KNOWLEDGE_BASE_PATH=./Dr_Gupt_Knowledge_Base.pdf
🌍 Impact
Problem Solved:

72% of rural patients consult quacks due to stigma (Source: Knowledge Base PDF)

Reduces reliance on unverified "roadside tent" practitioners

Demo Script:

"Meri shaadi mein 5 din hai... AI se baat karoon? Koi insaan nahi jaane ga?"

📂 Project Structure
dr-gupt/
├── assets/                 # Images/videos
├── knowledge_base/         # Medical FAQs
├── app.py                  # Main backend
├── clinic_lookup.py        # Location tools
└── appointment_booking.py  # Practo integration


 How to Contribute
Expand Knowledge Base: Add medical Q&A pairs in Hindi

Improve Tools: Enhance clinic lookup accuracy

Localize: Add more regional dialects



📜 License
MIT License | © 2024 Dr. Gupt Team

text

---

### Formatting Notes:  
1. Replace placeholder images with your actual screenshots (e.g., `![Demo](demo.png)`)  
2. Update GitHub repo link  
3. Add real API keys to `.env` in deployment (excluded here for security)  
4. For Mermaid diagram support, enable GitHub Markdown extensions  

Let me know if you'd like to emphasize any specific section (e.g., **bounty tracks** or **challenges faced**) for competition submissions!
