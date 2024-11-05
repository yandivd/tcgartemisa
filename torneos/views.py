from django.shortcuts import redirect, render
from .models import *

def index(request):
    if request.method == 'POST':
        tournament_date = request.POST.get('date') # Por defecto 4 si no se especifica
        
        tournament = Tournament.objects.create(
            date=tournament_date,
            status='Created'  # Estado inicial del torneo
        )
        
        # Redirigir a la página del torneo o mostrar mensaje de éxito
        return redirect('index')
    return render(request, 'index.html')


