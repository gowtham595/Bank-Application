from django.shortcuts import render
from bankapp.models import reg
from bankapp.forms import regform
from django.contrib import messages
from bankapp.forms import balform
from bankapp.forms import depform
from bankapp.forms import withdrawform
from bankapp.forms import transferform
from bankapp.forms import closeform
# Create your views here.
def homepage(request):
    return render(request,"home.html")

def newregpage(request):
    form=regform()
    if request.method=="POST":
        form=regform(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"ACCOUNT IS CREATED")
            return render(request,"newacc.html",{"form":form})
        else:
            messages.error(request,"Account is not created")
            return render(request,"newacc.html",{"form":form})
    return render(request,"newacc.html",{"form":form})

def balpage(request):
    form=balform()
    if request.method=="POST":
        form=balform(request.POST)
        if form.is_valid():
            accno=int(request.POST['accno'])
            password=request.POST['password']
            try:
                user=reg.objects.get(accno=accno,password=password)
                balance=user.amount
                return render(request,"balanceout.html",{"balance":balance,"accno":accno})
            except reg.DoesNotExist:
                messages.error(request,"Invalid account details")
                return render(request,"balance.html",{"form":form})
    return render(request,"balance.html",{"form":form})

def deppage(request):
    form=depform()
    if request.method == "POST":
        form=depform(request.POST)
        if form.is_valid():
            accno=int(request.POST['accno'])
            password=request.POST['password']
            deposit=int(request.POST['deposit'])
            try:
                user=reg.objects.get(accno=accno,password=password)
                balance=user.amount
                newbalance=balance+deposit
                user.amount=newbalance
                user.save()
                messages.success(request,"deposit success")
                return render(request,"depout.html",{"balance":balance,"newbalance":newbalance,"deposit":deposit})
            except reg.DoesNotExist:
                messages.error(request,"Invalid account details")
                return render(request,"deposit.html",{"form":form})
    return render(request,"deposit.html",{"form":form})

def drawpage(request):
    form=withdrawform
    if request.method=="POST":
        form=withdrawform(request.POST)
        if form.is_valid():
            accno=int(request.POST['accno'])
            password=request.POST['password']
            withdraw=float(request.POST['withdraw'])
            try:
                    user=reg.objects.get(accno=accno,password=password)
                    balance=user.amount
                    if withdraw <= balance:
                        newbalance=balance-withdraw
                        user.amount=newbalance
                        user.save()
                        messages.success(request,"Your withdrawl is Succesfull")
                        return render(request,"withdrawlout.html",{"balance":balance,"withdraw":withdraw,"newbalance":newbalance})
                    else:
                        return render(request,"withdraw.html","Insufficient funds in your account")
            except reg.DoesNotExist:
                    messages.error(request,"invalid credentials")
                    return render(request,"withdraw.html",{"form":form})
    return render(request,"withdraw.html",{"form":form})

def transferPage(request):
    form=transferform()
    if request.method == "POST":
        form=transferform(request.POST)
        if form.is_valid():
            accno=int(form.cleaned_data['accno'])
            name=form.cleaned_data['name']
            password=form.cleaned_data['password']
            target_account=int(form.cleaned_data['target_account'])
            amount=float(form.cleaned_data['amount'])
            try:
                user1=reg.objects.get(accno=accno,password=password,name=name)
                user2=reg.objects.get(accno=target_account)
                if not (user1.active and user2.active):
                    messages.error(request,"One of the Accounts is Deactivated....You can't Transfer Money")
                    return render(request, "transfer.html", {"form": form})
                else:
                    name2=user2.name
                    old_bal1=user1.amount
                    old_bal2=user2.amount
                    if old_bal1>=amount:
                        new_bal1=old_bal1-amount
                        new_bal2=old_bal2+amount
                        user1.amount=new_bal1
                        user2.amount=new_bal2
                        user1.save()
                        user2.save()
                        return render(request,"transferout.html",{"name2":name2,"name":name,"old_bal1":old_bal1,"amount":amount,"new_bal1":new_bal1,"old_bal2":old_bal2,"new_bal2":new_bal2})
                    else:
                        messages.error(request,"Insuficient Funds in your Account")
                        return render(request,"transfer.html",{"name":name,"form":form})
            except reg.DoesNotExist:
                messages.error(request,"Invalid Account Number or Password")
    return render(request,"transfer.html",{"form":form})

def deletepage(request):
    form=closeform()
    if request.method == "POST":
        form=closeform(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            accno = int(form.cleaned_data['accno'])
            password = form.cleaned_data['password']
            try:
                user = reg.objects.get(accno=accno,name=name,password=password)
                if not user.active:
                    messages.error(request,"Account is already Deactivated....")
                    return render(request, "delete.html", {"form": form})
                user.active = False
                user.save()
                messages.success(request,"Account Deactivated Successfully")
                return render(request,"deleteout.html",{"name":name,"accno":accno})
            except reg.DoesNotExist:
                messages.error(request,"Invalid Account Number or Password")
    return render(request,"delete.html",{"form":form})
    

def aboutpage(request):
    return render(request,"about.html")