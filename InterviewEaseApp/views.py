from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import os
import json
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import InterviewSerializer, AnswerSerializer, FeedbackReportSerializer
from Authentication.models import signupModel as User
from Authentication.views import verify_token
from .models import Interview, Questions, Answers, Domain
import google.generativeai as genai 

# Create your views here.

@csrf_exempt
@api_view(['POST'])
def create_interview(request):
    # Verify JWT token
    user_id, error_response = verify_token(request)
    if error_response:
        return error_response  # Return error if token is invalid

    # Get the authenticated user
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

    # Parse the form data using JSONParser for request data
    data = json.loads(request.body.decode('utf-8'))
    data['user'] = user.id  # Add user ID to data explicitly

    if "interview_type" in data.keys():
        filename = f'{data["domain"]}.json'
        file_path = os.path.join(settings.BASE_DIR, 'InterviewEaseBackend', 'media', filename)
        a = data.pop("interview_type")
        try:
            with open(file_path, 'r') as file:
                questions = json.load(file)
                data["questions"] = questions[0]["questions"]
        except FileNotFoundError:
            return JsonResponse({'error': 'Question file not found.'}, status=404)
                # Initialize the InterviewSerializer with data
        print(data)
        serializer = InterviewSerializer(data=data)
        if serializer.is_valid():
            # print(serializer)
            interview = serializer.save()
            return Response({'status': 'success', 'interview_id': interview.id}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status':'error', 'message':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    else:
        # Initialize the InterviewSerializer with data
        serializer = InterviewSerializer(data=data)
        if serializer.is_valid():
            # print(serializer)
            interview = serializer.save()
            return Response({'status': 'success', 'interview_id': interview.id}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status':'error', 'message':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



@csrf_exempt
def Get_questions(request, domain):
    if request.method == 'GET':

        filename = f'{domain}.json'
        file_path = os.path.join(settings.BASE_DIR, 'InterviewEaseBackend', 'media', filename)

        try:
            with open(file_path, 'r') as file:
                questions = json.load(file)
        except FileNotFoundError:
            return JsonResponse({'error': 'Question file not found.'}, status=404)
        
        if questions:
            questionList = []
            for question in questions:
                questionList.append(question['question'])

            return JsonResponse({'questions': questionList}, status=200)
        else:
            return JsonResponse({'error': 'Question not found.'}, status=404)
        

# @csrf_exempt
# def getQuestions(request, interview_id):
#     if request.method == "GET":
#         # Fetch the index from query parameters
#         question_index = request.GET.get("index", 0)
#         try:
#             question_index = int(question_index)
#         except ValueError:
#             return JsonResponse({"status": 400, "message": "Invalid index format"}, status=400)

#         # For hardcoded interview types
#         # predefined_interviews = ['SD', 'PM', 'HR', 'CD', 'DS']
#         # if interview_id in predefined_interviews:
#         #     filename = f'{interview_id}.json'
#         #     file_path = os.path.join(settings.BASE_DIR, 'InterviewEaseBackend', 'media', filename)

#         #     try:
#         #         with open(file_path, 'r') as file:
#         #             questions = json.load(file)
#         #     except FileNotFoundError:
#         #         return JsonResponse({'status': 404, 'message': 'Question file not found.'}, status=404)

#         #     if 0 <= question_index < len(questions):
#         #         return JsonResponse({
#         #             "status": 200,
#         #             "question": questions[question_index][str(question_index)],
#         #             "index": question_index,
#         #             "total_questions": len(questions)
#         #         })
#         #     else:
#         #         return JsonResponse({'status': 400, 'message': 'Invalid question index'}, status=400)

#         # # For custom interviews
#         # else:
#         try:
#             interview = Interview.objects.get(pk=interview_id)
#         except Interview.DoesNotExist:
#             return JsonResponse({"status": 404, "message": "Interview not found"}, status=404)
#         questions = Questions.objects.filter(interview=interview).order_by('id')
#         if 0 <= question_index < len(questions):
#             question = questions[question_index]
#             return JsonResponse({
#                 "status": 200,
#                 "question": question.question_text,
#                 "index": question_index,
#                 "total_questions": len(questions),
#                 "questionId":question.id
#             })
#         else:
#             return JsonResponse({'status': 400, 'message': 'Invalid question index'}, status=400)

#     return JsonResponse({"status": 405, "message": "Method not allowed"}, status=405)


@csrf_exempt
@api_view(['GET'])
def get_questions(request, interview_id):
    try:
        # 🔹 Parse the index from query params
        question_index = request.GET.get("index", 0)
        try:
            question_index = int(question_index)
        except ValueError:
            return Response({"status": 400, "message": "Invalid index format"}, status=400)

        # 🔹 Fetch interview
        try:
            interview = Interview.objects.get(pk=interview_id)
        except Interview.DoesNotExist:
            return Response({"status": 404, "message": "Interview not found"}, status=404)

        # 🔹 Get ordered questions for this interview
        questions = Questions.objects.filter(interview=interview).order_by("id")
        print(questions)

        if not questions:
            return Response({"status": 404, "message": "No questions found for this interview"}, status=404)

        # 🔹 Validate index range
        if 0 <= question_index < len(questions):
            question = questions[question_index]
            return Response({
                "question_text": question.question_text,
                "question_index": question_index,
                "total_questions": len(questions),
                "question_id": question.id,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"status": 400, "message": "Invalid question index"}, status=400)

    except Exception as e:
        return Response({"status": 500, "message": "Server error", "error": str(e)}, status=500)




@csrf_exempt
@api_view(['POST'])
def save_answer(request):
    if request.method == 'POST':
        user_id, error_response = verify_token(request)
        if error_response:
            return error_response 
        data=request.data
        newData = {
            "question": data["questionId"],
            "interview": data.get("interviewId"),  # Use .get() to handle null/optional values
            "answer_text": data.get("answer_text", ""),  # Default to an empty string if not provided
            "audio_path": data.get("audio_path"),  # Use .get() for optional fields
        }
        print(newData)
        serializer = AnswerSerializer(data=newData)
        
        # Validate input
        if serializer.is_valid():
            serializer.save()  # Save the validated data
            return Response(
                {
                    "message": "Answer saved successfully",
                    "status": "success",
                    # "data": {
                    #     "id": answer.id,
                    #     "question": answer.question.question_text,
                    #     "interview": answer.interview.id if answer.interview else None,
                    #     "answer_text": answer.answer_text,
                    #     "audio_path": answer.audio_path.url if answer.audio_path else None,
                    # },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

    return Response({"error": "Invalid HTTP method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@api_view(['GET'])
def get_answers(request, interview_id):
    try:
        # Verify user token
        user_id, error_response = verify_token(request)
        if error_response:
            return error_response
        
        # Fetch the interview
        interview = Interview.objects.get(pk=interview_id)
        
        # Fetch all answers related to this interview
        answers = Answers.objects.filter(interview=interview)

        # Prepare the response data
        answer_list = [
            {
                "id": answer.id,
                "question": answer.question.question_text,
                "answer_text": answer.answer_text,
                "audio_path": request.build_absolute_uri(answer.audio_path.url),
            }
            for answer in answers
        ]
        
        return JsonResponse(
            {"status": 200, "message": "Answers retrieved successfully", "answers": answer_list},
            status=200,
        )
    
    except Interview.DoesNotExist:
        return JsonResponse({"status": 404, "message": "Interview not found"}, status=404)
    
    except Exception as e:
        return JsonResponse(
            {"status": 500, "message": "An error occurred", "error": str(e)},
            status=500,
        )



# Configure Gemini with API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

@csrf_exempt
@api_view(['POST'])
def generate_interview_questions(request):
    try:
        # 🔹 Verify JWT token
        user_id, error_response = verify_token(request)
        if error_response:
            return error_response

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # 🔹 Get input from frontend
        domain_name = request.data.get("domain")
        difficulty = request.data.get("difficulty", "Easy")
        mode = request.data.get("mode_of_interview", "domain")

        if not domain_name:
            return Response({"error": "Domain is required"}, status=400)
        

        # 🔹 Generate questions (for domain mode)
        questions_list = []
        if mode == "domain":

            
            domain, _ = Domain.objects.get_or_create(domain=domain_name)

            model = genai.GenerativeModel("gemini-2.5-flash-lite")
            prompt = f"""
You are an expert interview question generator.

Task:
Generate exactly 1 interview questions for a candidate applying for the role of "{domain_name}" 
with a difficulty level of "{difficulty}".

Rules:
- Questions must match the role/domain "{domain_name}".
- Adjust complexity according to difficulty:
  * Easy → basic concepts and definitions
  * Medium → practical, scenario-based
  * Hard → complex, problem-solving/system design
- Keep each question short and clear.
- Return ONLY valid JSON in this format:

{{
  "questions": [
    {{ "question_text": "..." }},
    {{ "question_text": "..." }},
    {{ "question_text": "..." }},
    {{ "question_text": "..." }},
    {{ "question_text": "..." }}
  ]
}}
"""
            response = model.generate_content(prompt)
            raw_text = response.text.strip()

            if raw_text.startswith("```"):
                raw_text = raw_text.strip("```").replace("json", "", 1).strip()

            try:
                parsed = json.loads(raw_text)
                questions_list = parsed.get("questions", [])
            except json.JSONDecodeError:
                questions_list = [{"question_text": raw_text}]

        # 🔹 Prepare serializer data
        data = {
            "user": user.id,
            "domain": domain.domain,   # serializer expects domain as string
            "difficulty": difficulty,
            "questions": questions_list,
        }

        # 🔹 Save with serializer
        print(data)
        serializer = InterviewSerializer(data=data)
        if serializer.is_valid():
            interview = serializer.save()
            return Response(
                {
                    "status": "success",
                    "interview_id": interview.id,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response({"status": "error", "errors": serializer.errors}, status=400)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


HESITATION_WORDS = ["hmm", "um", "uh", "umm", "like", "you know", "i think", "maybe", "sort of"]

def check_confidence(answer_text: str):
    text = answer_text.lower()
    hesitation_count = sum(text.count(word) for word in HESITATION_WORDS)
    
    if hesitation_count == 2:
        return "Confident"
    elif hesitation_count <= 5:
        return "Slightly hesitant"
    else:
        return "Hesitant"


@csrf_exempt
@api_view(['POST'])
def evaluate_answer(request):
    try:
        user_id, error_response = verify_token(request)
        if error_response:
            return error_response

        question_text = request.data.get("question_text")
        answer_text = request.data.get("answer_text")

        if not question_text or not answer_text:
            return Response({"error": "Both question_text and answer_text are required"}, status=400)

        # 1️⃣ Get text feedback from Gemini
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Detect tone using filler words
        voice_confidence = check_confidence(answer_text)

        # Use improved AI prompt
        prompt = f"""
        You are an experienced interview coach. 
        Evaluate the candidate’s answer in context.

        Question: {question_text}
        Answer: {answer_text}

        Evaluation Rules:
        - Be honest but encouraging (human-like tone).
        - If the answer is confident and accurate, acknowledge it.
        - If hesitation or filler words are present, gently mention it.
        - Highlight only the most important area(s) of improvement.
        - Keep feedback short (2–3 sentences).
        - Return the result in JSON format with these keys:
        {{
          "status": "success",
          "Tone": "{voice_confidence}",
          "Feedback": "Overall appreciation and insights",
          "Area of Improvement": "1–2 key things to improve"
        }}
        Only return valid JSON, nothing else.
        """

        response = model.generate_content(prompt)
        import json
        try:
            text_feedback = json.loads(response.text)
        except:
            text_feedback = {"raw_feedback": response.text}

        return Response({
            "status": "success",
            "text_feedback": text_feedback,
            "voice_feedback": {
                "confidence_level": voice_confidence
            }
        }, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@csrf_exempt
@api_view(['GET'])
def feedback_report(request):
    try:
        interview_id = request.GET.get("interview_id")
        if not interview_id:
            return Response({"status": "error", "message": "interview_id is required"}, status=400)
        
        interview = Interview.objects.get(pk=interview_id)
        answers = Answers.objects.filter(interview=interview).select_related("question")

        all_text = "\n".join([
            f"Q: {ans.question.question_text}\nA: {ans.answer_text or '[No Answer]'}"
            for ans in answers
        ])

        # Send to AI
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        prompt = f"""
You are an interviewer giving final feedback to a candidate after a mock interview. 
Your tone must be professional, constructive, and encouraging — just like a human interviewer.

Rules:
- Base your feedback ONLY on the transcript provided. 
- If the candidate's performance was excellent and you see no clear weaknesses, 
  say "No major weaknesses observed" instead of inventing one. 
- For area_of_improvement and suggestions, write "No immediate improvements needed" 
  if there is nothing important to suggest. 
- Keep sentences short and clear (1–2 sentences max).

Return ONLY valid JSON with these 5 fields:

{{
  "confidence": "Confident | Slightly Hesitant | Hesitant",
  "strengths": "Sentence or two about strengths",
  "weaknesses": "Sentence or two about weaknesses OR 'No major weaknesses observed'",
  "area_of_improvement": "Sentence or two OR 'No immediate improvements needed'",
  "suggestions": "Sentence or two OR 'Keep practicing to maintain current performance'"
}}

Transcript: {all_text}

"""

        response = model.generate_content(prompt)
        feedback_text = response.text.strip()
        if feedback_text.startswith("```"):
                feedback_text = feedback_text.strip("```").replace("json", "", 1).strip()

        try:
            parsed_feedback = json.loads(feedback_text)
        except json.JSONDecodeError:
            parsed_feedback = {
                "confidence": None,
                "strengths": None,
                "weaknesses": None,
                "area_of_improvement": None,
                "suggestions": None,
            }
        
        parsed_feedback["interview"] = interview.id

        # 🔹 Save or update FeedbackReport
        serializer = FeedbackReportSerializer(data=parsed_feedback)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response({"status": "error", "message": serializer.errors}, status=400)
        return Response({
            "status": "success",
            "feedback": parsed_feedback
        }, status = status.HTTP_201_CREATED)

    except Interview.DoesNotExist:
        return Response({"status": "error", "message": "Interview not found"}, status=404)
