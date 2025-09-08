from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

try:
    llm = ChatOllama(model="llama3.2:3b", temperature=0.7)
    print("Using Ollama (local LLM)")
except Exception as e:
    print(f"Ollama not available: {e}")
    print("Falling back to OpenAI...")
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

print("--- Direct Call ---")
direct_response = llm.invoke("What is the capital of Japan?")
print(direct_response.content)

prompt = ChatPromptTemplate.from_template(
    "Translate this sentence into {language}: {text}"
)
formatted_messages = prompt.format_messages(language="English", text="গ্রাম-পজিটিভ জীবাণু দ্বারা সৃষ্ট সংক্রমণের চিকিৎসায় ক্লক্সাসিলিন নির্দেশিত। পেনিসিলিনেজ উৎপাদনক্ষম স্টেফাইলোকক্কাই জনিত সংক্রমণের চিকিৎসায়ও এটি নির্দেশিত। এ জাতীয় সংক্রমণের মধ্যে রয়েছেঃ স্কিন ও সফ্‌ট টিস্যু সংক্রমণ : ফোঁড়া (boils), পূজাশয় (abscess), কার্বাংকল, ফারানকুলোসিস, সেলুলাইটিস, সংক্রমিত ক্ষত (infected wounds), সংক্রমিত পোড়া (infected burns), ত্বক প্রতিস্থাপন প্রতিরক্ষা (protection for skin grafts), ত্বকের বিভিন্ন সংক্রমণ যেমন আলসার, একজিমা ও একনি। রেসপিরেটরী ট্র্যাক্ট, নাক, কান ও গলার সংক্রমণ : নিউমোনিয়া, ফুসফুসের পূজাশয় (lung abscess), এমপায়েমা, সাইনোসাইটিস, ফ্যারিনজাইটিস, টনসিলাইটিস, কুইনসি, অটাইটিস মিডিয়া ও এক্সটারণা। ক্লক্সাসিলিন-সংবেদনশীল (sensitive), জীবাণু জনিত অন্যান্য সংক্রমণ : অসটিওমায়েলাইটিস, এনটেরাইটিস, এনডোকারডাইটিস, ইউরিনারী ট্র্যাক্ট সংক্রমণ ও সেপটিসেমিয়া।")
template_response = llm.invoke(formatted_messages)
print(template_response.content)

chain = prompt | llm | StrOutputParser()
chain_response = chain.invoke({"language": "French", "text": "The weather is nice today."})
print(chain_response)
