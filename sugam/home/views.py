from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import DocSummarized, ComikifyModel
from .GenerateFollowup import GenerateFollowup
from .VoiceToText import VoiceToText
from .ImageToText import ImageToText
from .Summarizer import Summarizer
from .Comikify import Comikify
from pprint import pprint 

openai_key = "sk-proj-z1UUgdiGJOozf4iNZFQ1T3BlbkFJBr4HrmgjphLfOQ06Es67"

def index(request):
    return render(request, "index.html")

@csrf_exempt
def upload(request):
    if request.method == 'GET':
        # Assuming the image is sent as a file in the 'image' field
        extracted_txt = request.GET.get('text')
        language = request.GET.get('lang')
        print("Text: ", extracted_txt)

        # Process the image and extract the text
        # img_to_txt =  ImageToText(uploaded_image)
        # extracted_txt = img_to_txt.start()
        
        try:
            summarize =  Summarizer(extracted_txt, openai_key, language)
            summarized_txt = summarize.start()
        except Exception as e: 
            summarized_txt = f"Error: {e}"

        doc_sum = DocSummarized(original_txt=extracted_txt, summarized_txt=summarized_txt)
        doc_sum.save()

        # Create the JSON response
        response_data = {
            'text': summarized_txt,
            'id': doc_sum.id,
        }

        return JsonResponse(response_data)

    # Handle other HTTP methods (e.g., GET) if needed
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def follow_up(request):
    if request.method == 'POST':
        doc_id = request.GET.get('id')
        extracted_question = request.GET.get('text')
        language = request.GET.get('lang')

        doc = DocSummarized.objects.get(id=doc_id)
        original_text = doc.original_txt

        # Process the voice and extract the question text
        # voice_to_text =  VoiceToText(uploaded_voice)
        # extracted_question = voice_to_text.start()

        try:
            gen_follow_up = GenerateFollowup(original_text, openai_key, language)
            follow_up = gen_follow_up.start(extracted_question)
        except Exception as e:
            follow_up = f"Error: {e}"

        # Create the JSON response
        response_data = {
            'followup': follow_up,  
        }
        pprint(response_data)

        return JsonResponse(response_data)

    # Handle other HTTP methods (e.g., PUT, DELETE) if needed
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def comikify(request):
    if request.method == 'GET':
        topic = request.GET.get('topic')
        language = request.GET.get('lang')
        print("Topic: ", topic)
        
        try:
            comikify = ComikifyModel.objects.get(topic=topic)
            result = comikify.result
            total = len(result)
        except ComikifyModel.DoesNotExist:
            # Call Comikify module to generate result list
            # Assuming `start()` method returns the result list
            comikify = Comikify(topic, openai_key, language)
            result = comikify.start()
            total = len(result)
            
            # Save the result and topic to the database
            ComikifyModel(topic=topic, result=result).save()

        data = {
            'result': result,
            'total': total
        }

        pprint(data)
        
        return JsonResponse(data)
