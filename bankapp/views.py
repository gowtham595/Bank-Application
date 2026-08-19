from django.shortcuts import render
from django.db import transaction
from django.contrib import messages
from bankapp.models import reg, Transaction
from bankapp.forms import regform, balform, depform, withdrawform, transferform, closeform


def homepage(request):
    return render(request, "home.html")


def newregpage(request):
    form = regform()
    if request.method == "POST":
        form = regform(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Account created successfully! Welcome to CBI Bank.")
            return render(request, "newacc.html", {"form": regform()})
        else:
            messages.error(request, "Please correct the errors below.")
    return render(request, "newacc.html", {"form": form})


def balpage(request):
    form = balform()
    if request.method == "POST":
        form = balform(request.POST)
        if form.is_valid():
            accno = int(form.cleaned_data['accno'])
            password = form.cleaned_data['password']
            try:
                user = reg.objects.get(accno=accno)
                if not user.active:
                    messages.error(request, "This account has been deactivated.")
                    return render(request, "balance.html", {"form": form})
                if not user.verify_password(password):
                    messages.error(request, "Invalid password.")
                    return render(request, "balance.html", {"form": form})
                return render(request, "balanceout.html", {
                    "balance": user.amount,
                    "accno": accno,
                    "name": user.name
                })
            except reg.DoesNotExist:
                messages.error(request, "Invalid account details.")
    return render(request, "balance.html", {"form": form})


def deppage(request):
    form = depform()
    if request.method == "POST":
        form = depform(request.POST)
        if form.is_valid():
            accno = int(form.cleaned_data['accno'])
            password = form.cleaned_data['password']
            deposit = float(form.cleaned_data['deposit'])
            try:
                user = reg.objects.get(accno=accno)
                if not user.active:
                    messages.error(request, "This account has been deactivated.")
                    return render(request, "deposit.html", {"form": form})
                if not user.verify_password(password):
                    messages.error(request, "Invalid password.")
                    return render(request, "deposit.html", {"form": form})

                old_balance = user.amount
                new_balance = old_balance + deposit
                user.amount = new_balance
                user.save()

                Transaction.objects.create(
                    account=user,
                    transaction_type='DEPOSIT',
                    amount=deposit,
                    balance_after=new_balance,
                    description=f"Cash deposit of ₹{deposit}"
                )

                messages.success(request, "Deposit successful!")
                return render(request, "depout.html", {
                    "balance": old_balance,
                    "newbalance": new_balance,
                    "deposit": deposit,
                    "accno": accno
                })
            except reg.DoesNotExist:
                messages.error(request, "Invalid account details.")
    return render(request, "deposit.html", {"form": form})


def drawpage(request):
    form = withdrawform()
    if request.method == "POST":
        form = withdrawform(request.POST)
        if form.is_valid():
            accno = int(form.cleaned_data['accno'])
            password = form.cleaned_data['password']
            withdraw = float(form.cleaned_data['withdraw'])
            try:
                user = reg.objects.get(accno=accno)
                if not user.active:
                    messages.error(request, "This account has been deactivated.")
                    return render(request, "withdraw.html", {"form": form})
                if not user.verify_password(password):
                    messages.error(request, "Invalid password.")
                    return render(request, "withdraw.html", {"form": form})

                balance = user.amount
                if withdraw > balance:
                    messages.error(request, "Insufficient funds in your account.")
                    return render(request, "withdraw.html", {"form": form})

                new_balance = balance - withdraw
                user.amount = new_balance
                user.save()

                Transaction.objects.create(
                    account=user,
                    transaction_type='WITHDRAW',
                    amount=withdraw,
                    balance_after=new_balance,
                    description=f"Cash withdrawal of ₹{withdraw}"
                )

                messages.success(request, "Your withdrawal is successful!")
                return render(request, "withdrawlout.html", {
                    "balance": balance,
                    "withdraw": withdraw,
                    "newbalance": new_balance,
                    "accno": accno
                })
            except reg.DoesNotExist:
                messages.error(request, "Invalid credentials.")
    return render(request, "withdraw.html", {"form": form})


@transaction.atomic
def transferPage(request):
    form = transferform()
    if request.method == "POST":
        form = transferform(request.POST)
        if form.is_valid():
            accno = int(form.cleaned_data['accno'])
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']
            target_account = int(form.cleaned_data['target_account'])
            amount = float(form.cleaned_data['amount'])

            try:
                user1 = reg.objects.select_for_update().get(accno=accno, name=name)
                user2 = reg.objects.select_for_update().get(accno=target_account)

                if not user1.active or not user2.active:
                    messages.error(request, "One of the accounts is deactivated. Transfer cannot proceed.")
                    return render(request, "transfer.html", {"form": form})

                if not user1.verify_password(password):
                    messages.error(request, "Invalid password.")
                    return render(request, "transfer.html", {"form": form})

                old_bal1 = user1.amount
                old_bal2 = user2.amount

                if old_bal1 < amount:
                    messages.error(request, "Insufficient funds in your account.")
                    return render(request, "transfer.html", {"form": form})

                new_bal1 = old_bal1 - amount
                new_bal2 = old_bal2 + amount

                user1.amount = new_bal1
                user2.amount = new_bal2
                user1.save()
                user2.save()

                Transaction.objects.create(
                    account=user1,
                    transaction_type='TRANSFER_OUT',
                    amount=amount,
                    balance_after=new_bal1,
                    description=f"Transfer to {user2.name} ({target_account})"
                )
                Transaction.objects.create(
                    account=user2,
                    transaction_type='TRANSFER_IN',
                    amount=amount,
                    balance_after=new_bal2,
                    description=f"Transfer from {user1.name} ({accno})"
                )

                messages.success(request, "Transfer completed successfully!")
                return render(request, "transferout.html", {
                    "name2": user2.name,
                    "name": name,
                    "old_bal1": old_bal1,
                    "amount": amount,
                    "new_bal1": new_bal1,
                    "old_bal2": old_bal2,
                    "new_bal2": new_bal2,
                    "target_account": target_account
                })
            except reg.DoesNotExist:
                messages.error(request, "Invalid account number or password.")
    return render(request, "transfer.html", {"form": form})


def deletepage(request):
    form = closeform()
    if request.method == "POST":
        form = closeform(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            accno = int(form.cleaned_data['accno'])
            password = form.cleaned_data['password']
            try:
                user = reg.objects.get(accno=accno, name=name)
                if not user.verify_password(password):
                    messages.error(request, "Invalid password.")
                    return render(request, "delete.html", {"form": form})
                if not user.active:
                    messages.error(request, "Account is already deactivated.")
                    return render(request, "delete.html", {"form": form})

                user.active = False
                user.save()
                messages.success(request, "Account deactivated successfully.")
                return render(request, "deleteout.html", {"name": name, "accno": accno})
            except reg.DoesNotExist:
                messages.error(request, "Invalid account number or password.")
    return render(request, "delete.html", {"form": form})


def aboutpage(request):
    return render(request, "about.html")