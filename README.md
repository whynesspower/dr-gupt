![image](https://github.com/user-attachments/assets/15aa42fd-6ab3-4fa3-8467-4e10845b6bc2)



# Dr. Gupt - AI-Powere![dr-gupt22](https://github.com/user-attachments/assets/155f399d-fd5b-422e-942c-3df026402b15)
AI agent for the next billion people. AI for bharat.   

Demo Video: https://youtu.be/zdJBMn49P6Q

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

![dr-gupt2](https://github.com/user-attachments/assets/9b973603-eedc-4d81-9ee9-d82f287f9c3c)


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

Building for the interest of MeiTy
![image](https://github.com/user-attachments/assets/f6aeb6c2-5cdd-4b50-952c-ca3b89870750)


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
