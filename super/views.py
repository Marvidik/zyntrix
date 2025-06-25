# views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import InvestmentPlan,PaymentMethods
from .serializers import InvestmentPlanSerializer,PaymentMethodSerializer

@api_view(['GET'])
def list_investment_plans(request):
    plans = InvestmentPlan.objects.all()
    serializer = InvestmentPlanSerializer(plans, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def list_payment_methods(request):
    methods = PaymentMethods.objects.all()
    serializer = PaymentMethodSerializer(methods, many=True)
    return Response(serializer.data)