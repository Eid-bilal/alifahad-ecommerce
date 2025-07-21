import json
import random
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Wallet, WalletTransactions, SpinHistory


@login_required(login_url='login')
@csrf_exempt
def spin_wheel(request):
    
    if request.method == 'POST':
        try: 
            # Predefined reward possibilities
            rewards = [
                {'amount': 5.00, 'probability': 0.3},   # 30% chance
                {'amount': 10.00, 'probability': 0.2},  # 20% chance
                {'amount': 20.00, 'probability': 0.15}, # 15% chance
                {'amount': 50.00, 'probability': 0.1},  # 10% chance
                {'amount': 100.00, 'probability': 0.05},# 5% chance
                {'amount': 0.00, 'probability': 0.2}    # 20% chance of no reward
            ]

            # Select reward based on weighted probability
            total = sum(r['probability'] for r in rewards)
            r = random.uniform(0, total)
            upto = 0
            for reward in rewards:
                if upto + reward['probability'] >= r:
                    chosen_reward = reward['amount']
                    break
                upto += reward['probability']

            # Update user's wallet and log spin
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            wallet.balance += chosen_reward
            wallet.save()

            # Log spin history
            SpinHistory.objects.create(
                user=request.user, 
                reward_amount=chosen_reward, 
                is_won=chosen_reward > 0
            )

            WalletTransactions.objects.create(
                user=request.user,
                amount=chosen_reward,
                transaction_type=WalletTransactions.SPIN,
                description=f"Earned reward from spin: ₹{chosen_reward:.2f}",
                wallet=wallet,
            )

            return JsonResponse({
                'success': True,
                'reward': chosen_reward,
                'message': f'Congratulations! You won ₹{chosen_reward:.2f}'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Error processing spin.',
                'error': str(e)
            })
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required(login_url='login')
def user_wallet(request):
    """
    Render the user's wallet page.
    """
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    context = {
        "balance": wallet.balance
    }
    return render(request, "user/wallet.html", context)

#-------------- Wallet Transaction history ----------------------------------------------------------------
from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def transaction_history(request):
    # Query for the user's transactions
    transactions = WalletTransactions.objects.filter(user=request.user).order_by('-timestamp')
    
    # Set up pagination
    paginator = Paginator(transactions, 100)  # Show 10 transactions per page
    page_number = request.GET.get('page')  # Get the current page number from the query string
    page_obj = paginator.get_page(page_number)
    
    # Render the page with the transactions and pagination
    return render(request, 'user/wallet_trans.html', {'page_obj': page_obj})
