from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer, pipeline
from torch.nn.functional import softmax
import time

# TODO: write a longer test for this
# Load the quantized ONNX model
quantized_model = ORTModelForSequenceClassification.from_pretrained(
    "./backend/app/onnx_model", file_name="model_quantized.onnx"
)
tokenizer = AutoTokenizer.from_pretrained("./backend/app/onnx_model")

long_texts = [
    """The quick brown fox jumps over the lazy dog. This is a classic example used to test font styles and other typographical elements in typesetting. This sentence contains all the letters in the English language.""",
    """Artificial intelligence is transforming industries by automating processes and providing insights through data analysis. However, concerns over data privacy and ethical implications remain challenges that need to be addressed.""",
    """The integration of AI into healthcare has shown promise in early diagnosis of diseases, personalized medicine, and efficient healthcare management. Despite this, regulatory hurdles and ethical questions about data usage persist.""",
    """The development of autonomous vehicles is revolutionizing transportation. While the potential benefits include reduced accidents and enhanced efficiency, the technology also raises concerns about job displacement and safety during transitions.""",
    """The rise of large language models like GPT and DistilBERT has revolutionized natural language processing tasks, enabling advancements in chatbots, sentiment analysis, and content generation. However, their environmental impact and ethical concerns must be addressed.""",
    'fuck you'
]


start_time = time.time()
# Example text for inference
for text in long_texts:
    inputs = tokenizer(text, return_tensors="pt")

    # Run inference
    outputs = quantized_model(**inputs)
    logits =  outputs.logits
    probabilities = softmax(logits, dim=1)[0]
    predicted_class = probabilities.argmax(dim=-1).item()
    print("Probabilities:", probabilities)
onx_time = time.time() - start_time
print(onx_time)

model = pipeline("text-classification", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")
start_time = time.time()
for text in long_texts:
    tmp = model(text)
    print(tmp)

hf_time = time.time() - start_time
print(hf_time)

#  => onx model for the win