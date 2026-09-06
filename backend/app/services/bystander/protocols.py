"""
Bystander First Aid Protocols Database
Provides structured, step-by-step emergency instructions across 10 critical scenarios
with multi-language translation support (English, Hindi, Marathi, Tamil, Telugu, Bengali).
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi (हिंदी)",
    "mr": "Marathi (मराठी)",
    "ta": "Tamil (தமிழ்)",
    "te": "Telugu (తెలుగు)",
    "bn": "Bengali (বাংলা)"
}

PROTOCOLS_DATABASE: Dict[str, Dict[str, Any]] = {
    "cpr": {
        "id": "cpr",
        "title": "Cardiopulmonary Resuscitation (CPR)",
        "category": "cardiac",
        "severity": "critical",
        "compression_rate_bpm": "100-120 compressions per minute",
        "compression_ratio": "30 compressions : 2 rescue breaths",
        "icon": "❤️",
        "video_url": "https://www.youtube.com/watch?v=0kH-SspnnyA",
        "translations": {
            "en": {
                "title": "CPR (Cardiopulmonary Resuscitation)",
                "summary": "Immediate chest compressions for unresponsive victims without normal breathing.",
                "key_stats": "Compression Rate: 100-120 bpm | Depth: 2-2.4 inches (5-6 cm)",
                "steps": [
                    "Check scene safety and confirm victim is unresponsive and not breathing normally.",
                    "Call emergency dispatch immediately and send someone to retrieve an AED.",
                    "Place heel of one hand on center of chest (lower half of sternum), interlock second hand on top.",
                    "Push hard and fast at a rate of 100-120 compressions/minute (to rhythm of 'Stayin Alive').",
                    "Allow chest to recoil completely between compressions.",
                    "If trained, give 2 rescue breaths after every 30 compressions until AED or EMS arrives."
                ],
                "warnings": "Do not stop compressions unless victim revives or EMS takes over."
            },
            "hi": {
                "title": "सीपीआर (कार्डियोपुलमोनरी रीससिटेशन)",
                "summary": "सांस न लेने वाले बेहोश पीड़ित के लिए तत्काल छाती को दबाने की प्रक्रिया।",
                "key_stats": "दबाव की दर: 100-120 प्रति मिनट | गहराई: 2-2.4 इंच",
                "steps": [
                    "स्थान की सुरक्षा जांचें और पुष्टि करें कि पीड़ित बेहोश है और सामान्य रूप से सांस नहीं ले रहा है।",
                    "तुरंत आपातकालीन नंबर पर कॉल करें और किसी को एईडी (AED) लाने भेजें।",
                    "एक हाथ की हथेली छाती के केंद्र में रखें और दूसरे हाथ की उंगलियां उसमें फंसाएं।",
                    "100-120 प्रति मिनट की गति से छाती को मजबूती से और तेजी से दबाएं।",
                    "हर दबाव के बाद छाती को पूरी तरह वापस ऊपर आने दें।",
                    "यदि प्रशिक्षित हैं, तो हर 30 बार दबाने के बाद 2 बार मुंह से सांस दें।"
                ],
                "warnings": "जब तक एम्बुलेंस न आ जाए या पीड़ित होश में न आ जाए, सीपीआर न रोकें।"
            },
            "mr": {
                "title": "सीपीआर (कार्डियोपल्मनरी रिससिटेशन)",
                "summary": "छाती दाबण्याची आणीबाणीची प्रक्रिया.",
                "key_stats": "दाबाचा वेग: १००-१२० प्रति मिनिट",
                "steps": [
                    "सुरक्षिततेची खात्री करा आणि पीडित व्यक्तीचा श्वास तपासा.",
                    "तातडीने मदत मागवा आणि AED मागवा.",
                    "छातीच्या मध्यभागी तळहात ठेवून जोराने दाबा.",
                    "दर मिनिटाला १०० ते १२० वेळा दाबा.",
                    "३० वेळा दाबल्यानंतर २ वेळा तोंडाने श्वास द्या."
                ],
                "warnings": "मदत येईपर्यंत सीपीआर थांबवू नका."
            },
            "ta": {
                "title": "சிபிஆர் (CPR முதலுதவி)",
                "summary": "சுவாசம் இல்லாத நபருக்கு நெஞ்சை அழுத்தும் முதலுதவி.",
                "key_stats": "அழுத்த வேகம்: நிமிடத்திற்கு 100-120 முறை",
                "steps": [
                    "பாதிக்கப்பட்டவர் சுயநினைவின்றி உள்ளாரா என சரிபார்க்கவும்.",
                    "உடனடி அவசர உதவிக்கு அழைக்கவும்.",
                    "நெஞ்சின் நடுவில் கைகளை வைத்து வேகமாக அழுத்தவும்.",
                    "நிமிடத்திற்கு 100-120 முறை அழுத்தவும்.",
                    "30 அழுத்தங்களுக்குப் பின் 2 முறை செயற்கை சுவாசம் அளிக்கவும்."
                ],
                "warnings": "மருத்துவ குழு வரும் வரை நிறுத்த வேண்டாம்."
            },
            "te": {
                "title": "సిపిఆర్ (CPR ప్రథమ చికిత్స)",
                "summary": "శ్వాస లేని బాధితుడికి ఛాతీ నొక్కే విధానం.",
                "key_stats": "నొక్కే వేగం: నిమిషానికి 100-120 సార్లు",
                "steps": [
                    "బాధితుడు స్పృహలో ఉన్నాడో లేడో తనిఖీ చేయండి.",
                    "వెంటనే అత్యవసర సహాయానికి కాల్ చేయండి.",
                    "ఛాతీ మధ్యలో చేతులు ఉంచి వేగంగా నొక్కండి.",
                    "నిమిషానికి 100-120 సార్లు క్రమం తప్పకుండా నొక్కండి."
                ],
                "warnings": "అంబులెన్స్ వచ్చే వరకు సిపిఆర్ ఆపవద్దు."
            },
            "bn": {
                "title": "সিপিআর (CPR প্রথম চিকিৎসা)",
                "summary": "শ্বাসহীন অজ্ঞানের জন্য বুকের চাপ দেওয়ার পদ্ধতি।",
                "key_stats": "চাপের গতি: প্রতি মিনিটে ১০০-১২০ বার",
                "steps": [
                    "আক্রান্ত ব্যক্তি সচেতন কিনা পরীক্ষা করুন।",
                    "অবিলম্বে জরুরি নম্বরে কল করুন।",
                    "বুকের মাঝে হাত রেখে দ্রুত ও শক্তভাবে চাপ দিন।",
                    "প্রতি মিনিটে ১০০-১২০ বার চাপ দিন।",
                    "৩০ বার চাপের পর ২ বার কৃত্রিম শ্বাস দিন।"
                ],
                "warnings": "ডাক্তার না আসা পর্যন্ত সিপিআর থামাবেন না।"
            }
        }
    },

    "bleeding_control": {
        "id": "bleeding_control",
        "title": "Severe Bleeding & Tourniquet Application",
        "category": "trauma",
        "severity": "critical",
        "icon": "🩸",
        "video_url": "https://www.youtube.com/watch?v=StopTheBleed",
        "translations": {
            "en": {
                "title": "Bleeding Control & Tourniquet Application",
                "summary": "Control life-threatening hemorrhage using direct pressure, trauma dressing, or tourniquet.",
                "key_stats": "Tourniquet Placement: 2-3 inches above wound (never over a joint)",
                "steps": [
                    "Apply firm, continuous direct pressure with sterile gauze or clean cloth over the wound.",
                    "If bleeding does not stop or is spurting from an arm/leg, apply a commercial tourniquet 2-3 inches above the wound.",
                    "Tighten windlass rod until bleeding stops completely and pulse below tourniquet is absent.",
                    "Secure windlass in clip and write exact application TIME on victim's forehead or tourniquet strap.",
                    "Keep victim warm with blanket and monitor for shock while awaiting EMS."
                ],
                "warnings": "Never loosen or remove a tourniquet once applied. EMS must remove it."
            },
            "hi": {
                "title": "अत्यधिक रक्तस्राव नियंत्रण एवं टूर्निकेट उपयोग",
                "summary": "गंभीर ब्लीडिंग को रोकने के लिए दबाव और टूर्निकेट का प्रयोग करें।",
                "key_stats": "टूर्निकेट लगाने का स्थान: घाव से 2-3 इंच ऊपर (जोड़ पर न लगाएं)",
                "steps": [
                    "घाव पर साफ कपड़े या गॉज से सीधा और तेज दबाव बनाएं।",
                    "यदि हाथ या पैर से खून का फव्वारा छूट रहा हो, तो घाव से 2-3 इंच ऊपर टूर्निकेट बांधें।",
                    "टूर्निकेट की पट्टी को तब तक कसें जब तक खून बहना पूरी तरह बंद न हो जाए।",
                    "पट्टी कसने का सटीक समय टूर्निकेट या पीड़ित के माथे पर लिखें।",
                    "पीड़ित को गर्म रखें और एम्बुलेंस का इंतजार करें।"
                ],
                "warnings": "एक बार टूर्निकेट बांधने के बाद उसे ढीला न करें।"
            },
            "mr": {
                "title": "रक्तस्राव नियंत्रण आणि टुरनिकेट",
                "summary": "गंभीर रक्तस्राव थांबवण्याची पद्धत.",
                "key_stats": "जखमेच्या २-३ इंच वर टुरनिकेट बांधा",
                "steps": [
                    "जखमेवर स्वच्छ कपड्याने जोराने दाबा.",
                    "रक्त थांबत नसल्यास जखमेच्या वर टुरनिकेट बांधा.",
                    "रक्तस्राव पूर्ण बंद होईपर्यंत टुरनिकेट कसा.",
                    "टुरनिकेट बांधल्याची वेळ नोंदवा."
                ],
                "warnings": "टुरनिकेट एकदा बांधल्यावर सोडता कामा नये."
            },
            "ta": {
                "title": "இரத்தப்போக்கு கட்டுப்பாடு",
                "summary": "கடும் இரத்தப்போக்கை நிறுத்தும் முதலுதவி.",
                "key_stats": "காயத்திற்கு 2-3 அங்குலம் மேலே கட்டவும்",
                "steps": [
                    "காயத்தின் மீது துணியை வைத்து அழுத்தவும்.",
                    "இரத்தம் நிற்காவிட்டால் டூர்னிக்கெட் (Tourniquet) பட்டையை கட்டவும்.",
                    "இரத்தம் நிற்கும் வரை இறுக்கவும்.",
                    "கட்டிய நேரத்தை குறித்து வைத்துக்கொள்ளவும்."
                ],
                "warnings": "கட்டிய பட்டையை தளர்த்த வேண்டாம்."
            },
            "te": {
                "title": "రక్తస్రావం నివారణ",
                "summary": "తీవ్రమైన రక్తస్రావాన్ని అదుపుచేసే విధానం.",
                "key_stats": "గాయానికి 2-3 అంగుళాల పైన కట్టండి",
                "steps": [
                    "గాయంపై శుభ్రమైన గుడ్డతో గట్టిగా నొక్కండి.",
                    "రక్తం ఆగకపోతే టూర్నికేట్ కట్టు కట్టండి.",
                    "రక్తస్రావం పూర్తిగా ఆగే వరకు తిప్పండి.",
                    "కట్టిన సమయాన్ని నమోదు చేయండి."
                ],
                "warnings": "ఒక్కసారి కట్టిన తర్వాత విప్పకూడదు."
            },
            "bn": {
                "title": "রক্তপাত নিয়ন্ত্রণ",
                "summary": "মারাত্মক রক্তক্ষরণ বন্ধ করার প্রথম চিকিৎসা।",
                "key_stats": "ক্ষতস্থানের ২-৩ ইঞ্চি উপরে ব্যান্ডেজ বাঁধুন",
                "steps": [
                    "ক্ষতস্থানে পরিষ্কার কাপড় দিয়ে শক্ত করে চাপ দিন।",
                    "রক্ত বন্ধ না হলে উপরে শক্ত ব্যান্ডেজ বাঁধুন।",
                    "রক্তপাত সম্পূর্ণ বন্ধ হওয়া পর্যন্ত কষুন।",
                    "ব্যান্ডেজ বাঁধার সময় লিখে রাখুন।"
                ],
                "warnings": "ব্যান্ডেজ আলগা করবেন না।"
            }
        }
    },

    "burn_treatment": {
        "id": "burn_treatment",
        "title": "Burn Injury Treatment",
        "category": "thermal",
        "severity": "high",
        "icon": "🔥",
        "video_url": "https://www.youtube.com/watch?v=BurnFirstAid",
        "translations": {
            "en": {
                "title": "Burn Treatment (Cooling & Covering)",
                "summary": "Cool the burn immediately with clean water and cover loosely.",
                "key_stats": "Cooling Time: 10 to 20 minutes under cool running water",
                "steps": [
                    "Cool burn area immediately under cool running water for 10-20 minutes. Do NOT use ice.",
                    "Remove clothing or jewelry near the burn before swelling starts (unless stuck to burn).",
                    "Cover burn loosely with sterile non-stick bandage or clean cling-wrap.",
                    "Keep victim warm to prevent hypothermia if large burns are present.",
                    "Administer pain relief if conscious and seek urgent medical evaluation for severe burns."
                ],
                "warnings": "Do NOT pop blisters, apply ice, toothpaste, or butter to burns."
            },
            "hi": {
                "title": "जले का इलाज (ठंडा करना एवं ढकना)",
                "summary": "जले हुए स्थान को तुरंत साफ ठंडे पानी से ठंडा करें और ढकें।",
                "key_stats": "पानी बहने का समय: 10 से 20 मिनट",
                "steps": [
                    "जले हुए हिस्से को 10-20 मिनट तक बहते ठंडे पानी के नीचे रखें। बर्फ का उपयोग न करें।",
                    "सूजन आने से पहले जले हिस्से के पास के कपड़े या गहने हटा दें।",
                    "जले स्थान को साफ सूती कपड़े या स्टेराइल पट्टी से ढीला ढकें।",
                    "पीड़ित को ठंडा होने से बचाएं और गर्म रखें।",
                    "गंभीर जलन के मामले में तुरंत डॉक्टर से संपर्क करें।"
                ],
                "warnings": "फफोले न फोड़ें, और जले पर टूथपेस्ट, मक्खन या बर्फ न लगाएं।"
            },
            "mr": {
                "title": "भाजल्यावरील उपचार",
                "summary": "भाजलेला भाग थंड पाण्याने धुवा.",
                "key_stats": "१० ते २० मिनिटे थंड पाणी टाका",
                "steps": [
                    "भाजलेल्या भागावर १०-२० मिनिटे थंड पाणी टाका.",
                    "दागिने किंवा घट्ट कपडे काढा.",
                    "स्वच्छ कपड्याने सैलसर झाका."
                ],
                "warnings": "बर्फ, टूथपेस्ट किंवा लोणी लावू नका."
            },
            "ta": {
                "title": "தீக்காய முதலுதவி",
                "summary": "தீக்காயத்தை குளிர்ந்த நீரால் குளிர வைக்கவும்.",
                "key_stats": "10-20 நிமிடங்கள் நீரின்கீழ் வைக்கவும்",
                "steps": [
                    "10-20 நிமிடங்கள் ஓடும் குளிர்ந்த நீரில் காட்டவும்.",
                    "ஆடைகள் மற்றும் நகைகளை அகற்றுங்கள்.",
                    "சுத்தமான துணியால் லேசாக மூடவும்."
                ],
                "warnings": "பனிக்கட்டி அல்லது பேஸ்ட் தடவ வேண்டாம்."
            },
            "te": {
                "title": "కాలిన గాయాల చికిత్స",
                "summary": "గాయాన్ని వెంటనే చల్లని నీటితో కడగండి.",
                "key_stats": "10-20 నిమిషాలు చల్లని నీటి కింద ఉంచండి",
                "steps": [
                    "10-20 నిమిషాలు గాయాన్ని చల్లని నీటితో కడగండి.",
                    "ఆభరణాలు, బిగుతు బట్టలు తొలగించండి.",
                    "శుభ్రమైన గుడ్డతో వదులుగా కప్పండి."
                ],
                "warnings": "ఐస్ లేదా టూత్‌పేస్ట్ రాయకూడదు."
            },
            "bn": {
                "title": "পোড়া আঘাতের চিকিৎসা",
                "summary": "পোড়া স্থান ঠান্ডা জলে ধুয়ে দিন।",
                "key_stats": "১০-২০ মিনিট ঠান্ডা জল ঢালুন",
                "steps": [
                    "১০-২০ মিনিট ঠান্ডা জলের নিচে রাখুন।",
                    "গয়না বা শক্ত কাপড় খুলে ফেলুন।",
                    "পরিষ্কার কাপড় দিয়ে হালকা করে ঢেকে দিন।"
                ],
                "warnings": "বরফ বা পেস্ট লাগাবেন না।"
            }
        }
    },

    "choking": {
        "id": "choking",
        "title": "Choking Relief (Heimlich Maneuver)",
        "category": "airway",
        "severity": "critical",
        "icon": "🗣️",
        "video_url": "https://www.youtube.com/watch?v=HeimlichManeuver",
        "translations": {
            "en": {
                "title": "Choking Relief (Heimlich Maneuver)",
                "summary": "Clear severe airway obstruction using back blows and abdominal thrusts.",
                "key_stats": "Ratio: 5 Back Blows : 5 Abdominal Thrusts",
                "steps": [
                    "Ask 'Are you choking?' If victim cannot speak or cough, stand behind them.",
                    "Give 5 sharp back blows between shoulder blades using heel of your hand.",
                    "If unreleased, place fist slightly above victim's navel, grasp with other hand.",
                    "Perform 5 quick, upward abdominal thrusts into the abdomen.",
                    "Repeat 5 back blows and 5 abdominal thrusts until object is expelled or victim becomes unconscious.",
                    "If victim becomes unconscious, lower to ground and begin CPR compressions."
                ],
                "warnings": "For pregnant women or obese victims, perform chest thrusts instead of abdominal thrusts."
            },
            "hi": {
                "title": "दम घुटने का इलाज (हाइमलिक मैन्युवर)",
                "summary": "सांस की नली में फंसी चीज को पीठ पर थपकी और पेट के दबाव से निकालें।",
                "key_stats": "अनुपात: 5 पीठ पर थपकी : 5 पेट पर दबाव",
                "steps": [
                    "पूछें 'क्या आपका दम घुट रहा है?' यदि वे बोल न सकें, तो उनके पीछे खड़े हों।",
                    "हथेली के निचले हिस्से से कंधों के बीच 5 बार पीठ पर थपकी दें।",
                    "यदि वस्तु न निकले, तो नाभि के ठीक ऊपर मुट्ठी रखें और दूसरी हथेली से पकड़ें।",
                    "पेट में ऊपर और अंदर की ओर 5 बार तेजी से दबाव दें।",
                    "वस्तु निकलने तक 5 थपकी और 5 दबाव की प्रक्रिया दोहराएं।"
                ],
                "warnings": "गर्भवती महिलाओं के लिए पेट के बजाय छाती पर दबाव दें।"
            },
            "mr": {
                "title": "घशात अडकल्यास उपाय (हाइमलिच)",
                "summary": "पाठीवर मारणे आणि पोटावर दाब देणे.",
                "key_stats": "५ पाठीवर मारा : ५ पोटावर दाबा",
                "steps": [
                    "पाठीवर ५ वेळा जोराने मारा.",
                    "नाभीच्या वर मूठ ठेवून मागे ओढा (५ वेळा).",
                    "गोष्ट बाहेर येईपर्यंत पुनरावृत्ती करा."
                ],
                "warnings": "गरोदर स्त्रियांसाठी छातीवर दाब द्या."
            },
            "ta": {
                "title": "மூச்சுத்திணறல் முதலுதவி",
                "summary": "தொண்டையில் அடைத்த பொருளை எடுக்கும் முறை.",
                "key_stats": "5 முறை முதுகில் தட்டுதல் : 5 முறை வயிற்றில் அழுத்துதல்",
                "steps": [
                    "முதுகில் 5 முறை வேகமாக தட்டுங்கள்.",
                    "தொப்புளுக்கு மேல் கையை வைத்து உள்ளே அழுத்துங்கள்.",
                    "பொருள் வெளியேறும் வரை தொடருங்கள்."
                ],
                "warnings": "கர்ப்பிணிகளுக்கு நெஞ்சில் அழுத்தவும்."
            },
            "te": {
                "title": "ఉపిరి ఆడకపోవడం (హైమ్లిచ్)",
                "summary": "గొంతులో అడ్డుపడినదాన్ని తొలగించే విధానం.",
                "key_stats": "5 సార్లు వీపుపై తట్టడం : 5 సార్లు పొట్టపై నొక్కడం",
                "steps": [
                    "వీపుపై 5 సార్లు గట్టిగా తట్టండి.",
                    "బొడ్డు పైన పిడికిలి ఉంచి లోపలికి లాగండి.",
                    "వస్తువు బయటకు వచ్చే వరకు కొనసాగించండి."
                ],
                "warnings": "గర్భిణులకు ఛాతీపై నొక్కాలి."
            },
            "bn": {
                "title": "গলায় কিছু আটকানোর চিকিৎসা",
                "summary": "গলায় আটকে থাকা বস্তু বের করার নিয়ম।",
                "key_stats": "৫ বার পিঠে থাপ্পড় : ৫ বার পেটে চাপ",
                "steps": [
                    "পিঠের মাঝে ৫ বার জোরে থাপ্পড় দিন।",
                    "নাভির উপরে হাত রেখে ভিতরের দিকে চাপ দিন।",
                    "বস্তুটি বের না হওয়া পর্যন্ত চালান।"
                ],
                "warnings": "গর্ভবতী হলে বুকে চাপ দিন।"
            }
        }
    },

    "stroke_fast": {
        "id": "stroke_fast",
        "title": "Stroke Recognition (FAST Test)",
        "category": "neurological",
        "severity": "critical",
        "icon": "🧠",
        "video_url": "https://www.youtube.com/watch?v=StrokeFAST",
        "translations": {
            "en": {
                "title": "Stroke Recognition (FAST Test)",
                "summary": "Identify early stroke symptoms using Face, Arms, Speech, and Time.",
                "key_stats": "FAST: F=Face, A=Arms, S=Speech, T=Time to call 911",
                "steps": [
                    "F (Face): Ask person to smile. Check if one side of the face droops.",
                    "A (Arms): Ask person to raise both arms. Check if one arm drifts downward.",
                    "S (Speech): Ask person to repeat a simple sentence. Check for slurred or strange speech.",
                    "T (Time): If any of these signs are present, call emergency services IMMEDIATELY.",
                    "Keep victim calm, lying flat with head slightly elevated while awaiting ambulance."
                ],
                "warnings": "Do NOT give victim food, drinks, or aspirin."
            },
            "hi": {
                "title": "स्ट्रोक की पहचान (FAST टेस्ट)",
                "summary": "चेहरा, हाथ, बोली और समय (FAST) से स्ट्रोक का तुरंत पता लगाएं।",
                "key_stats": "F=चेहरा, A=हाथ, S=बोली, T=समय (तुरंत कॉल करें)",
                "steps": [
                    "F (चेहरा): व्यक्ति को मुस्कुराने कहें। क्या चेहरा एक तरफ लटक रहा है?",
                    "A (हाथ): दोनों हाथ उठाने कहें। क्या एक हाथ नीचे गिर रहा है?",
                    "S (बोली): एक साधारण वाक्य बोलने कहें। क्या आवाज हकला रही है?",
                    "T (समय): यदि कोई भी लक्षण दिखे, तो तुरंत 108/आपातकालीन नंबर पर कॉल करें।",
                    "मरीज को शांत रखें और सिर थोड़ा ऊंचा करके लिटाएं।"
                ],
                "warnings": "मरीज को पानी, खाना या एस्पिरिन न दें।"
            },
            "mr": {
                "title": "स्ट्रोक ओळखणे (FAST चाचणी)",
                "summary": "स्ट्रोकची लक्षणे त्वरित ओळखा.",
                "key_stats": "F=चेहरा, A=हात, S=बोलणे, T=वेळ",
                "steps": [
                    "F: हसण्यास सांगा (चेहरा वाकडा होतो का पहा).",
                    "A: दोन्ही हात वर करण्यास सांगा.",
                    "S: साधे वाक्य बोलण्यास सांगा.",
                    "T: लक्षणे दिसल्यास त्वरित एम्बुलन्स बोलवा."
                ],
                "warnings": "काहीही खाण्यास किंवा पिण्यास देऊ नका."
            },
            "ta": {
                "title": "பக்கவாதம் கண்டறிதல் (FAST)",
                "summary": "பக்கவாத அறிகுறிகளை விரைவாக கண்டறியும் முறை.",
                "key_stats": "F=முகம், A=கைகள், S=பேச்சு, T=நேரம்",
                "steps": [
                    "F: சிரிக்க சொல்லுங்கள் (முகம் கோணுகிறதா?).",
                    "A: இரு கைகளையும் உயர்த்த சொல்லுங்கள்.",
                    "S: பேச சொல்லுங்கள் (பேச்சு குளறுகிறதா?).",
                    "T: உடனடியாக அவசர உதவிக்கு அழையுங்கள்."
                ],
                "warnings": "உணவு அல்லது தண்ணீர் தர வேண்டாம்."
            },
            "te": {
                "title": "పక్షవాతం గుర్తింపు (FAST)",
                "summary": "పక్షవాతం లక్షణాలను గుర్తించే FAST పరీక్ష.",
                "key_stats": "F=ముఖం, A=చేతులు, S=మాట, T=సమయం",
                "steps": [
                    "F: నవ్వమని చెప్పండి (ముఖం పక్కకు వాలుతుందా?).",
                    "A: రెండు చేతులు ఎత్తమని చెప్పండి.",
                    "S: మాట్లాడమని చెప్పండి (మాట తొట్రూపడుతుందా?).",
                    "T: వెంటనే అంబులెన్స్‌కు కాల్ చేయండి."
                ],
                "warnings": "ఆహారం లేదా నీరు ఇవ్వవద్దు."
            },
            "bn": {
                "title": "স্ট্রোক সনাক্তকরণ (FAST পরীক্ষা)",
                "summary": "স্ট্রোকের লক্ষণ দ্রুত চেনার উপায়।",
                "key_stats": "F=মুখ, A=হাত, S=কথা, T=সময়",
                "steps": [
                    "F: হাসতে বলুন (মুখ বেঁকে যাচ্ছে কি?).",
                    "A: দুই হাত তুলতে বলুন।",
                    "S: কথা বলতে বলুন (কথা জড়াচ্ছে কি?).",
                    "T: লক্ষণ থাকলে এখনই অ্যাম্বুলেন্সে কল করুন।"
                ],
                "warnings": "জল বা খাবার দেবেন না।"
            }
        }
    },

    "snake_bite": {
        "id": "snake_bite",
        "title": "Snake Bite Protocol",
        "category": "environmental",
        "severity": "critical",
        "icon": "🐍",
        "video_url": "https://www.youtube.com/watch?v=SnakeBiteFirstAid",
        "translations": {
            "en": {
                "title": "Snake Bite Protocol",
                "summary": "Immobilize victim, minimize movement, and transport to anti-venom medical facility.",
                "key_stats": "Keep bitten limb immobile and below heart level",
                "steps": [
                    "Keep victim calm and completely still. Panic increases venom circulation.",
                    "Immobilize bitten limb with a splint below heart level.",
                    "Remove rings, watches, and tight clothing before swelling occurs.",
                    "Clean bite mark gently with clean soap and water. Cover with clean cloth.",
                    "Transport immediately to hospital equipped with Snake Anti-Venom (SAV)."
                ],
                "warnings": "Do NOT cut wound, suck venom, apply ice, or use tight tourniquets."
            },
            "hi": {
                "title": "सांप के काटने का प्रोटोकॉल",
                "summary": "पीड़ित को शांत रखें, अंग को हिलाएं नहीं और तुरंत अस्पताल पहुंचाएं।",
                "key_stats": "काटे गए अंग को हृदय के स्तर से नीचे रखें",
                "steps": [
                    "पीड़ित को शांत रखें। घबराने से जहर तेजी से फैलता है।",
                    "काटे गए अंग को स्थिर रखें और दिल के स्तर से नीचे रखें।",
                    "सूजन से पहले अंगूठी, घड़ी या कड़े उतार दें।",
                    "घाव को साफ पानी से धीरे से धोएं और साफ कपड़े से ढकें।",
                    "पीड़ित को तुरंत एंटी-वेनम (SAV) वाले अस्पताल ले जाएं।"
                ],
                "warnings": "घाव को काटें नहीं, जहर चूसने की कोशिश न करें और बर्फ न लगाएं।"
            },
            "mr": {
                "title": "सर्पदंश प्रथमोपचार",
                "summary": "रुग्णाला शांत ठेवा आणि हालचाल करू देऊ नका.",
                "key_stats": "दंश झालेला भाग हृदयाच्या खाली ठेवा",
                "steps": [
                    "रुग्णाला शांत ठेवा.",
                    "दंश झालेला भाग स्थिर ठेवा.",
                    "दागिने व घट्ट कपडे काढा.",
                    "तात्काळ सर्पबंधक (Anti-Venom) असलेल्या रुग्णालयात न्या."
                ],
                "warnings": "कापू नका किंवा चोखू नका."
            },
            "ta": {
                "title": "பாம்பு கடி முதலுதவி",
                "summary": "பாதிக்கப்பட்டவரை அசையாமல் மருத்துவமனைக்கு கொண்டு செல்லவும்.",
                "key_stats": "கடிபட்ட பகுதியை இதய மட்டத்திற்கு கீழே வைக்கவும்",
                "steps": [
                    "நபரை அமைதியாக இருக்க சொல்லுங்கள்.",
                    "கடிபட்ட கையை/காலை அசையாமல் வையுங்கள்.",
                    "நகைகளை அகற்றிவிடுங்கள்.",
                    "உடனடியாக மருத்துவமனைக்கு கொண்டு செல்லுங்கள்."
                ],
                "warnings": "காயத்தை அறுக்கவோ, உறிஞ்சவோ வேண்டாம்."
            },
            "te": {
                "title": "పాము కాటు ప్రథమ చికిత్స",
                "summary": "బాధితుడిని కదలకుండా ఉంచి అంబులెన్స్ పిలవండి.",
                "key_stats": "కాటు వేసిన భాగాన్ని గుండె స్థాయికి దిగువన ఉంచండి",
                "steps": [
                    "బాధితుడిని ప్రశాంతంగా ఉంచండి.",
                    "కాటు వేసిన అవయవాన్ని కదలకుండా ఉంచండి.",
                    "ఆభరణాలను తొలగించండి.",
                    "వెంటనే యాంటీ-వెనమ్ ఉన్న ఆసుపత్రికి తరలించండి."
                ],
                "warnings": "గాయాన్ని కోయవద్దు, విషాన్ని పీల్చవద్దు."
            },
            "bn": {
                "title": "সাপের কামড়ের চিকিৎসা",
                "summary": "রোগীকে শান্ত রেখে দ্রুত হাসপাতালে নিয়ে যান।",
                "key_stats": "আক্রান্ত অঙ্গ হৃদপিণ্ডের নিচে রাখুন",
                "steps": [
                    "রোগীকে শান্ত ও স্থির রাখুন।",
                    "আক্রান্ত অঙ্গ নাড়াচড়া করাবেন না।",
                    "গয়না বা ঘড়ি খুলে ফেলুন।",
                    "অ্যান্টি-ভেনমযুক্ত হাসপাতালে দ্রুত নিয়ে যান।"
                ],
                "warnings": "কাটবেন না বা মুখ দিয়ে বিষ চুষবেন না।"
            }
        }
    }
}


class ProtocolManager:
    """Manages protocol retrieval, language translation, and search filtering."""

    @staticmethod
    def get_protocol(protocol_id: str, lang: str = "en") -> Optional[Dict[str, Any]]:
        """Retrieve protocol by ID in specified language with fallback to English."""
        protocol = PROTOCOLS_DATABASE.get(protocol_id.lower())
        if not protocol:
            return None

        lang_code = lang.lower() if lang.lower() in SUPPORTED_LANGUAGES else "en"
        trans = protocol["translations"].get(lang_code) or protocol["translations"].get("en")

        return {
            "id": protocol["id"],
            "category": protocol["category"],
            "severity": protocol["severity"],
            "icon": protocol["icon"],
            "video_url": protocol.get("video_url"),
            "compression_rate_bpm": protocol.get("compression_rate_bpm"),
            "language": lang_code,
            "language_name": SUPPORTED_LANGUAGES.get(lang_code, "English"),
            "title": trans["title"],
            "summary": trans["summary"],
            "key_stats": trans.get("key_stats"),
            "steps": trans["steps"],
            "warnings": trans.get("warnings")
        }

    @staticmethod
    def list_all_protocols(lang: str = "en") -> List[Dict[str, Any]]:
        """List all available protocols in target language."""
        result = []
        for pid in PROTOCOLS_DATABASE.keys():
            item = ProtocolManager.get_protocol(pid, lang)
            if item:
                result.append(item)
        return result


# Singleton export
protocol_manager = ProtocolManager()
