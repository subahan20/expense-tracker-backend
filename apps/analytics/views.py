from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum
from apps.budgets.models import Budget
from apps.income.models import Income
from apps.expenses.models import Expense

class DashboardView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        if not user:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.first()

        if not user:
            return Response({"detail": "No users exist in DB"}, status=400)

        month_filter = request.query_params.get('month') # expected 'YYYY-MM'
        
        income_qs = Income.objects.filter(user=user)
        expense_qs = Expense.objects.filter(user=user)
        
        if month_filter:
            try:
                year, month = month_filter.split('-')
                income_qs = income_qs.filter(created_at__year=year, created_at__month=month)
                expense_qs = expense_qs.filter(created_at__year=year, created_at__month=month)
            except ValueError:
                pass # ignore invalid formats

        income_sum = income_qs.aggregate(Sum('amount'))['amount__sum'] or 0
        expense_sum = expense_qs.aggregate(Sum('amount'))['amount__sum'] or 0
        total_balance = income_sum - expense_sum

        try:
            budget = Budget.objects.get(user=user).monthly_budget
        except Budget.DoesNotExist:
            budget = 0

        # Recent transactions based on the filtered queryset
        recent_incomes = income_qs.order_by('-created_at')[:5]
        recent_expenses = expense_qs.order_by('-created_at')[:5]
        
        recent_transactions = []
        for inc in recent_incomes:
            recent_transactions.append({
                'id': str(inc.id),
                'type': 'income',
                'title': inc.source,
                'amount': inc.amount,
                'date': inc.created_at
            })
        for exp in recent_expenses:
            recent_transactions.append({
                'id': str(exp.id),
                'type': 'expense',
                'title': exp.title,
                'amount': -exp.amount,
                'date': exp.created_at
            })
            
        recent_transactions.sort(key=lambda x: x['date'], reverse=True)
        recent_transactions = recent_transactions[:5]

        # Aggregate expenses by category for the filtered month
        expenses_by_category = list(expense_qs.values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total'))
        
        # Format the response to match the frontend expectations
        formatted_categories = []
        for item in expenses_by_category:
            cat_name = item['category__name'] if item['category__name'] else 'Uncategorized'
            formatted_categories.append({
                'name': cat_name,
                'total': item['total']
            })

        return Response({
            'monthly_budget': budget,
            'total_income': income_sum,
            'total_expenses': expense_sum,
            'total_balance': total_balance,
            'recent_transactions': recent_transactions,
            'expenses_by_category': formatted_categories
        })

import os
import json
import urllib.request

def get_groq_api_key():
    key = os.environ.get('GROQ_API_KEY')
    if key:
        return key
    
    # try reading .env file in the backend root
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('GROQ_API_KEY='):
                    return line.split('=', 1)[1].strip()
    return None

class GroqAnalysisView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        api_key = get_groq_api_key()
        if not api_key:
            return Response({"error": "GROQ_API_KEY not found in .env file."}, status=400)
        
        income = request.data.get('total_income', 0)
        expenses = request.data.get('total_expenses', 0)
        categories = request.data.get('expenses_by_category', [])
        
        prompt = f"""
        You are an expert financial advisor. Analyze the following monthly budget data:
        Total Income: ₹{income}
        Total Expenses: ₹{expenses}
        Category Breakdown: {json.dumps(categories)}
        
        Provide concise, clear instructions to the user on where to reduce spending and how to increase savings. 
        Format your response as 3 to 4 short, punchy bullet points using markdown. Do not be overly wordy.
        """

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "You are a helpful, professional financial assistant. Provide actionable, concise advice."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 500
        }
        
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                ai_message = result['choices'][0]['message']['content']
                return Response({"analysis": ai_message})
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            return Response({"error": f"Groq API Error: {error_body}"}, status=500)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
