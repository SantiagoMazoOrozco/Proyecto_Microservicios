from django.shortcuts import render, redirect, get_object_or_404
from .models import Set
from .forms import SetForm

def set_create(request):
    if request.method == 'POST':
        form = SetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('set_list')
    else:
        form = SetForm()
    return render(request, 'consultas/sets/set_form.html', {'form': form})

def set_update(request, pk):
    set_instance = get_object_or_404(Set, pk=pk)
    if request.method == 'POST':
        form = SetForm(request.POST, instance=set_instance)
        if form.is_valid():
            form.save()
            return redirect('set_list')
    else:
        form = SetForm(instance=set_instance)
    return render(request, 'consultas/sets/set_form.html', {'form': form})

def set_delete(request, pk):
    set_instance = get_object_or_404(Set, pk=pk)
    if request.method == 'POST':
        set_instance.delete()
        return redirect('set_list')
    return render(request, 'consultas/sets/set_confirm_delete.html', {'set': set_instance})

def view_all_sets(request):
    sets = Set.objects.all()
    return render(request, 'consultas/sets/set_list.html', {'sets': sets})
