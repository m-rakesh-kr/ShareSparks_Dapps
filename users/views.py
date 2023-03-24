import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView
from web3 import Web3

from content.models import Content, ContentVersion, ContentRewards, Rewards
from content.utils import create_contract_instance, get_content_from_ipfs, MyCustomPaginator
from users import tasks
from users.forms import PasswordResetEmailForm, ProfileUpdateForm, UserForm, RegistrationForm
from users.models import CustomUser


class RegistrationView(CreateView):
    form_class = RegistrationForm

    def get(self, request, **kwargs):
        return render(request, 'users/register.html', {'title': 'Register'})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Congratulations! Your account has been registered. Please login to continue.")
            return redirect('login')
        return render(request, 'users/register.html', {'form': form, 'title': 'Register'})


class UserLoginView(View):
    form_class = AuthenticationForm

    def get(self, request):
        return render(request, 'users/login.html', {'title': 'Login'})

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if user := authenticate(request, username=username, password=password):
            login(request, user)
            return redirect('home')
        return render(request, 'users/login.html', {'error_message': 'Invalid login credentials'})


class SendPasswordResetMail(View):
    form_class = PasswordResetEmailForm
    template_name = 'users/send_password_reset_mail.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        # print(request.POST)
        form = self.form_class(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        email = request.POST.get('email')
        if user := CustomUser.objects.filter(email=email).first():
            tasks.send_password_reset_mail.delay(email=email, user_id=user.id)
            return redirect('password_reset_done')

        messages.error(request, 'User not Registered with this email! Please try with registered email!')
        return render(request, self.template_name, status=404)

        # try:
        #     user = CustomUser.objects.get(email=email)
        # except CustomUser.DoesNotExist:
        #     # Handle the exception here
        #     return render(request, self.template_name, {'form': form})
        # else:
        #     # If no exception occurs, continue with the code here
        #     tasks.send_password_reset_mail.delay(email=email, user_id=user.id)
        #     return redirect('password_reset_done')


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    form_class = ProfileUpdateForm
    model = CustomUser
    template_name = 'users/update_profile.html'

    def test_func(self):
        user = self.get_object()
        return self.request.user.id == user.id

    def get_success_url(self):
        user = self.get_object()
        return reverse_lazy('profile', args=[user.username])


class ProfileView(LoginRequiredMixin, ListView):
    template_name = 'users/profile.html'

    def get_queryset(self):
        return get_object_or_404(CustomUser, username=self.kwargs.get('username'), is_active=True)

    def get_context_data(self, **kwargs):
        # get_context_data method  provide additional data to the template beyond what is provided by the view's model
        # or queryset
        context = super().get_context_data(**kwargs)
        user = self.get_queryset()
        context['user_data'] = user
        context['total_posts'] = Content.objects.filter(user=user).count()

        ipfs_addresses = []
        if user.wallet_address:
            user_wallet_address = Web3.toChecksumAddress(user.wallet_address)
            contract = create_contract_instance()

            # fetch user's content addresses from blockchain
            ipfs_addresses = contract.functions.getIpfsHashes(user_wallet_address).call()

            # remove the older versions from the list
            user_content = ContentVersion.objects.filter(content_id__user_id=user)
            user_content_addresses = [content.ipfs_address for content in user_content]

            for user_content_address in user_content_addresses:
                if user_content_address in ipfs_addresses:
                    ipfs_addresses.remove(user_content_address)

            # remove the archived content
            archived_content = Content.objects.filter(is_archived=True, user=user)
            user_archived_addresses = [content.ipfs_address for content in archived_content]

            for user_archived_address in user_archived_addresses:
                if user_archived_address in ipfs_addresses:
                    ipfs_addresses.remove(user_archived_address)

            content_list = []
            ipfs_addresses = list(reversed(ipfs_addresses))

            for address in ipfs_addresses:
                # fetch content details from ipfs
                content_dict = get_content_from_ipfs(address)

                # if ipfs_data == 'error':
                #     context['error'] = 'error'
                #     return context
                #
                # content_dict = json.loads(ipfs_data)

                if len(content_dict['data']) >= 250:
                    clean_text = re.sub('<[^<]+?>', '', content_dict['data'])
                    content_dict['data'] = f"{clean_text[:250]}..."

                content_dict['user'] = user

                content_obj = get_object_or_404(Content, ipfs_address=address)
                content_dict['id'] = content_obj.id
                content_dict['post_time'] = content_obj.created_at

                if content_obj.is_updated:
                    content_dict['updated_time'] = content_obj.updated_at

                content_list.append(content_dict)

            context['posts'] = content_list
            paginator = MyCustomPaginator(content_list, 1)  # Display 3 items per page
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context['posts'] = paginator.get_paginated_items(page_obj.number, page_obj.paginator.per_page)
            context['page_obj'] = page_obj
        context['total_posts'] = len(ipfs_addresses)
        return context


class DeactivateUserView(LoginRequiredMixin, View):
    model = CustomUser
    form_class = UserForm

    def get(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return redirect('home')


class WalletView(View):
    def get(self, request):
        return render(request, 'users/wallet.html', {'title': 'Wallet'})

    def post(self, request):
        return redirect('transfer_spark_tokens')


class UserLogoutView(LoginRequiredMixin, View):

    def get(self, request):
        logout(request)
        return redirect('home')


class UserRewardsView(View):
    def get(self, request, **kwargs):
        user = CustomUser.objects.get(username=kwargs['username'])

        rewards = ContentRewards.objects.values('reward_id', 'reward__reward_badge').annotate(
            reward_count=Count('reward_id')).filter(content_id__user_id=user.id, is_rewarded=True)

        next_rewards = Rewards.objects.exclude(id__in=rewards.values('reward_id'))



        # # fetch all the rewards event from blockchain
        # contract = create_contract_instance()
        #
        # events = contract.events['GiveReward'].getLogs(
        #     fromBlock=0,
        #     argument_filters={'to': Web3.toChecksumAddress(request.user.wallet_address)}
        # )
        #
        # all_rewards = []
        # counter = 1
        #
        # for event in events:
        #     tokens_rewarded_in_wei = event['args']['value']
        #     tokens_rewarded = tokens_rewarded_in_wei / (10 ** 18)
        #
        #     tx_hash = event['transactionHash'].hex()
        #
        #     reward = {'counter': counter, 'tx_hash': tx_hash, 'tokens_rewarded': tokens_rewarded}
        #     all_rewards.append(reward)
        #     counter += 1

        context = {
            'title': 'Rewards',
            # 'event_rewards': all_rewards,
            'rewards': rewards,
            'next_rewards': next_rewards,
            'user': user
        }
        return render(request, 'users/user_rewards.html', context=context)


class RewardsTransactionView(View):
    def get(self, request, **kwargs):
        user_obj = CustomUser.objects.get(username=kwargs['username'])

        if content_rewards := ContentRewards.objects.filter(reward_id=kwargs['pk'], content__user=user_obj.id):
            content_reward = content_rewards[0].reward

            rewards = []
            for counter, reward in enumerate(content_rewards, start=1):
                ipfs_data = get_content_from_ipfs(reward.content.ipfs_address)
                reward_dict = {
                    'counter': counter,
                    'content_title': ipfs_data['title'],
                    'content_category': ipfs_data['category'],
                    'transaction_link': reward.transaction_link
                }
                rewards.append(reward_dict)
            context = {
                'rewards': rewards,
                'reward_token': content_reward.token,
                'reward_for': f'{content_reward.target} {content_reward.target_type}',
                'reward_badge': content_reward.reward_badge
            }
            return render(request, 'users/rewards_transaction.html', context)
        context = {
            'error': f'{user_obj.username} has not won any rewards under this category'
        }
        return render(request, 'users/rewards_transaction.html', context)

