import os
import math
import re

from django.contrib import messages

from django.db.models import ProtectedError
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView
from django.http import HttpResponse

from content.forms import ContentCategoryForm, RewardForm, AddContentForm, AddCommentForm
from content.models import ContentCategory, Rewards, Content, Likes, Comments, ContentVersion, ContentRewards
from dotenv import load_dotenv
from web3 import Web3

from content.utils import create_contract_instance, get_content_from_ipfs, get_contract_abi, create_web3_instance, \
    add_content_on_ipfs, get_list_of_content
from users.models import CustomUser

load_dotenv()

w3 = create_web3_instance()
contract = create_contract_instance()


class HomeView(ListView):
    template_name = 'content/home.html'

    def get_queryset(self):
        return Content.objects.filter(is_archived=False, user__is_active=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content_obj = self.get_queryset()
        page_number = self.request.GET.get('page')
        context = get_list_of_content(content_obj, context, page_number)
        return context


class AboutView(ListView):
    model = Rewards
    context_object_name = 'rewards'
    ordering = ['id']
    template_name = 'content/about_us.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'About'
        return context


# ajax functions for wallet features
class VerifyWalletAddress(View):
    def get(self, request):
        wallet_address = request.user.wallet_address

        if wallet_address:
            wallet_address = Web3.toChecksumAddress(wallet_address)

        return JsonResponse({'wallet_address': wallet_address})


class SaveWalletAddressView(View):
    def post(self, request):
        wallet_address = request.POST['account_address']
        user_address = request.user.wallet_address

        if not user_address:
            user = request.user
            user.wallet_address = wallet_address
            user.save()
        else:
            if wallet_address != Web3.toChecksumAddress(user_address):
                return JsonResponse({'status': False})
        return JsonResponse({'status': False})


class GetWalletDetailsView(LoginRequiredMixin, View):
    def get(self, request):
        user_wallet_address = request.user.wallet_address
        wallet_address = Web3.toChecksumAddress(user_wallet_address)
        matic_balance = w3.eth.get_balance(wallet_address)
        spark_balance = contract.functions.balanceOf(wallet_address).call()
        matic = matic_balance / math.pow(10, 18)
        spark = spark_balance / math.pow(10, 18)
        return JsonResponse(
            {'spark_balance': spark, 'wallet_address': wallet_address, 'matic_balance': matic})


# category
class AddCategoryView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'content/add_category.html'
    form_class = ContentCategoryForm
    success_url = reverse_lazy('home')
    model = ContentCategory
    success_message = 'New Category Added'

    def test_func(self):
        return bool(self.request.user.is_superuser)

    def post(self, request, *args, **kwargs):
        category = request.POST.get('category').lower()
        ContentCategory.objects.get_or_create(category=category)
        return redirect('view_categories')


class CategoryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'content/categories.html'
    model = ContentCategory
    context_object_name = 'categories'
    ordering = ['id']

    def test_func(self):
        return bool(self.request.user.is_superuser)


class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ContentCategory
    fields = ['category']
    template_name = 'content/update_category.html'
    success_url = reverse_lazy('view_categories')
    success_message = "Your profile is updated"

    def test_func(self):
        return bool(self.request.user.is_superuser)

    def get(self, request, pk):
        category = ContentCategory.objects.get(id=pk)
        return render(request, 'content/update_category.html', {'category': category.category})


class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, pk):
        try:
            category_obj = ContentCategory.objects.filter(id=pk)
            category_obj.delete()
            messages.success(request, "Category Deleted")
        except ProtectedError:
            messages.warning(request, "You cannot delete this category")
        return redirect('view_categories')

    def test_func(self):
        return bool(self.request.user.is_superuser)


# rewards
class RewardCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'content/add_rewards.html'
    success_url = reverse_lazy('view_rewards')
    success_message = 'Reward created'
    form_class = RewardForm

    def test_func(self):
        return bool(self.request.user.is_superuser)

    def form_valid(self, form):
        return super().form_valid(form)


class RewardsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'content/rewards.html'
    model = Rewards
    context_object_name = 'rewards'
    ordering = ['id']

    def test_func(self):
        return bool(self.request.user.is_superuser)


class RewardsUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'content/update_rewards.html'
    model = Rewards
    form_class = RewardForm
    success_url = reverse_lazy('view_rewards')

    def test_func(self):
        return bool(self.request.user.is_superuser)

    def get(self, request, *args, **kwargs):
        reward = Rewards.objects.get(id=kwargs.get('pk'))
        return render(request, 'content/update_rewards.html', {'reward': reward})


class RewardsDelete(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return bool(self.request.user.is_superuser)

    def get(self, request, pk):
        reward_obj = Rewards.objects.filter(id=pk)
        reward_obj.delete()
        return redirect('view_rewards')


# contract owner function
class UpdatePostFeeView(LoginRequiredMixin, View):
    def get(self, request):
        owner = contract.functions.getOwner().call()
        user_address = w3.toChecksumAddress(request.user.wallet_address)

        # verify if the current user is the contract owner
        if user_address == owner:
            current_fee_in_wei = contract.functions.getPostFee().call()
            current_fee = current_fee_in_wei / (10 ** 18)
            return render(request, 'content/update_post_fee.html', {'current_fee': current_fee})
        else:
            messages.error(request, "Sorry! Only the contract owner has the permission to update the post fees")
            return redirect('home')

    def post(self, request):
        new_fee_in_spk = float(request.POST.get('new_post_fee'))
        public_address = os.environ.get('PUBLIC_ADDRESS')
        chain_id = int(os.environ.get('CHAIN_ID'))

        new_fee_in_wei = new_fee_in_spk * (10 ** 18)
        new_fee = int(new_fee_in_wei)

        # build the transaction
        txn = contract.functions.setPostFee(new_fee).buildTransaction(
            {
                "chainId": hex(chain_id),
                "gasPrice": w3.eth.gas_price,
                "from": public_address,
                "nonce": w3.eth.getTransactionCount(public_address)
            }
        )

        # sign the transaction
        sign_txn = w3.eth.account.sign_transaction(txn, private_key=os.environ.get('PRIVATE_KEY'))

        # send the transaction to the blockchain
        send_txn = w3.eth.send_raw_transaction(sign_txn.rawTransaction)

        # wait for the transaction receipt
        txn_receipt = w3.eth.wait_for_transaction_receipt(send_txn)

        if txn_receipt['status'] == 1:
            print(txn_receipt, txn_receipt['status'])
            messages.success(request, "Post fees updated successfully")
        else:
            messages.error(request, "Post fees did not update due to some error. Please try again")
        return redirect('home')


# Content
class AddContentView(LoginRequiredMixin, View):
    categories = ContentCategory.objects.all()

    def get(self, request):
        form = AddContentForm()
        if request.user.wallet_address:
            user_address = w3.toChecksumAddress(request.user.wallet_address)
            user_balance = contract.functions.balanceOf(user_address).call()
            post_fee = contract.functions.getPostFee().call()

            if user_balance >= post_fee:
                context = {
                    'form': form,
                    'data': form['data'],
                    'categories': self.categories,
                    'user_address': Web3.toChecksumAddress(request.user.wallet_address),
                }
                return render(request, 'content/create_content.html', context=context)
            return redirect('add_spark_tokens')
        return redirect('wallet')

    def post(self, request):
        form = AddContentForm(request.POST)
        if form.is_valid():
            form_data = form.data
            title = form_data["title"]
            category_id = form_data["category"]
            data = form_data["data"]
            category = ContentCategory.objects.get(id=category_id)

            # storing the data on ipfs (Pinata)
            content_data = {'title': title, 'category': category.category, 'category_id': category_id, 'data': data}
            # print(f'contentdata--->{content_data}')
            ipfs = add_content_on_ipfs(content_data=content_data, username=request.user.username, title=title)
            # print(f'ipfs--->{ipfs}')

            context = {
                'ipfs_address': ipfs,
                'user_address': request.user.wallet_address,
                'category_id': category_id,
                'contract_address': os.environ.get('CONTRACT_ADDRESS'),
                'function': 'add'
            }

            return render(request, 'content/add_content_to_blockchain.html', context=context)

        user_address = w3.toChecksumAddress(request.user.wallet_address)

        return render(request, 'content/create_content.html', context={'errors': form.errors,
                                                                       'categories': self.categories,
                                                                       'user_address': user_address,
                                                                       'form': form,
                                                                       'data': form['data']})


class GetContractAbi(View):
    def get(self, request):
        return HttpResponse(get_contract_abi())


class AddContentDataInDatabase(View):
    def post(self, request, *args, **kwargs):
        data_dict = request.POST
        ipfs = data_dict['ipfs']
        category_id = data_dict['category_id']
        content = Content()
        content.ipfs_address = ipfs
        content.user = request.user
        content.category_id = category_id
        content.save()
        messages.success(request, "Content posted successfully")
        return JsonResponse({'status': 'success'})


class LikeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        content_id = kwargs.get('content_id')
        already_liked = Likes.objects.filter(content_id=content_id, user=request.user).all()
        if not already_liked:
            likes = Likes(content_id=content_id, user=request.user)
            likes.save()
        return redirect('view_detailed_post', content_id=content_id)


class UnlikeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        content_id = kwargs.get('content_id')
        like = Likes.objects.filter(content_id=content_id, user=request.user).first()
        like.delete()
        return redirect('view_detailed_post', content_id=content_id)


class ViewDetailedContent(LoginRequiredMixin, View):
    form_class = AddCommentForm

    def get(self, request, *args, **kwargs):
        content_id = kwargs.get('content_id')
        post = Content.objects.get(pk=content_id)

        alreadyliked_obj = Likes.objects.filter(user_id=request.user.id, content_id=content_id).all()
        already_liked = bool(alreadyliked_obj)
        likes_count = Likes.objects.filter(content_id=content_id).count()
        comments = Comments.objects.filter(content_id=content_id).exclude(user=post.user).order_by('-id')[:3]
        comments_count = Comments.objects.filter(content_id=content_id).count()
        post_time = post.created_at

        # fetch content creator's address from blockchain
        user_address = contract.functions.getIpfsAuthor(post.ipfs_address).call()
        user_obj = CustomUser.objects.get(wallet_address=user_address.lower())

        # fetch content details from ipfs
        content_data = get_content_from_ipfs(post.ipfs_address)

        context = {
            'content': content_data,
            'content_id': content_id,
            'content_creator': user_obj,
            'likes_count': likes_count,
            'comments_count': comments_count,
            'already_liked': already_liked,
            'post_time': post_time,
            'comments': comments
        }

        if post.is_updated:
            context['updated_time'] = post.updated_at

        return render(request, 'content/view_detailed_content.html', context=context)

    def post(self, request, *args, **kwargs):
        comment_form = self.form_class(request.POST)
        content_id = kwargs.get('content_id')
        if comment_form.is_valid():
            form_data = comment_form.data
            comment = form_data.get('comment')
            comment_obj = Comments(comment=comment, user=request.user, content_id=content_id)
            comment_obj.save()
            return redirect('view_comments', content_id=content_id)


class ViewComments(LoginRequiredMixin, View):
    def get(self, request, content_id):
        comments = Comments.objects.filter(content_id=content_id)
        total_comments = comments.all()
        return render(request, 'content/view_comments.html', context={'comments': total_comments})


class DeleteComment(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, pk):
        comment = Comments.objects.filter(id=pk).first()
        content_id = comment.content.id
        comment.delete()
        return redirect('view_detailed_post', content_id=content_id)

    def test_func(self):
        comment_id = self.kwargs['pk']
        comment_user = Comments.objects.filter(id=comment_id).first().user
        return self.request.user == comment_user


class UpdateContentView(LoginRequiredMixin, UserPassesTestMixin, View):
    form_class = AddContentForm

    def test_func(self):
        content_id = self.kwargs['content_id']
        content_owner = get_object_or_404(Content, pk=content_id).user
        return self.request.user == content_owner

    def get(self, request, content_id):
        form = AddContentForm()
        content_id = self.kwargs.get('content_id')
        content = get_object_or_404(Content, pk=content_id)
        user_address = w3.toChecksumAddress(request.user.wallet_address)
        user_balance = contract.functions.balanceOf(user_address).call()
        post_fee = contract.functions.getPostFee().call()

        # fetch content details from ipfs
        content_data = get_content_from_ipfs(content.ipfs_address)

        if user_balance >= post_fee:
            context = {
                'user_address': Web3.toChecksumAddress(request.user.wallet_address),
                'content': content_data,
                'form': form,
                'data': form['data'],
            }

            return render(request, 'content/update_content.html', context=context)
        return redirect('add_spark_tokens')

    def post(self, request, content_id):
        form = AddContentForm(request.POST)
        if form.is_valid():
            form_data = form.data
            title = form_data["title"]
            data = form_data["data"]
            category = form_data["category"]
            category_obj = ContentCategory.objects.get(category=category)
            category_id = category_obj.id

            # storing the data on ipfs (Pinata)
            content_data = {'title': title, 'category': category, 'category_id': category_id, 'data': data}
            ipfs = add_content_on_ipfs(content_data=content_data, username=request.user.username, title=title)

            context = {
                'ipfs_address': ipfs,
                'user_address': request.user.wallet_address,
                'category_id': category_id,
                'contract_address': os.environ.get("CONTRACT_ADDRESS"),
                'content_id': self.kwargs.get('content_id')
            }
            return render(request, 'content/add_content_to_blockchain.html', context=context)
        user_address = w3.toChecksumAddress(request.user.wallet_address)
        return render(request, 'content/update_content.html',
                      context={'errors': form.errors, 'user_address': user_address,
                               'form': form,
                               'data': form['data']})


class UpdateContentDataInDatabase(View):
    def get(self, request, *args, **kwargs):
        data_dict = request.GET
        ipfs = data_dict['ipfs']
        content_id = data_dict['content_id']
        content = Content.objects.get(id=content_id)
        old_ipfs = content.ipfs_address
        content.ipfs_address = ipfs
        content.is_updated = True
        content.save()

        if version_obj := ContentVersion.objects.filter(content_id=content_id).last():
            version_num = version_obj.version_number + 1
        else:
            version_num = 1
        content_version = ContentVersion(ipfs_address=old_ipfs, version_number=version_num, content_id=content_id)
        content_version.save()

        return JsonResponse({'status': 'success'})


class ArchiveContentView(LoginRequiredMixin, UserPassesTestMixin, View):
    model = Content

    def test_func(self):
        content_id = self.kwargs.get('content_id')
        content_user = Content.objects.filter(id=content_id).first().user
        return self.request.user == content_user

    def get(self, request, content_id):
        content_id = self.kwargs.get('content_id')
        content = Content.objects.filter(id=content_id).first()

        if content.is_archived:
            content.is_archived = False
        else:
            content.is_archived = True

        content.save()
        return redirect('profile', username=request.user.username)


class GetArchiveContentView(LoginRequiredMixin, ListView):

    def get(self, request, **kwargs):
        if request.user.wallet_address:
            user_address = Web3.toChecksumAddress(request.user.wallet_address)

            # fetch user's content addresses from blockchain
            ipfs_addresses = contract.functions.getIpfsHashes(user_address).call()

            # remove the older versions from the list
            user_content = ContentVersion.objects.filter(content_id__user_id=request.user.id)
            user_content_addresses = [content.ipfs_address for content in user_content]

            for user_content_address in user_content_addresses:
                if user_content_address in ipfs_addresses:
                    ipfs_addresses.remove(user_content_address)

            # remove the unarchived content
            archived_content = Content.objects.filter(is_archived=False, user=request.user)
            user_archived_addresses = [content.ipfs_address for content in archived_content]

            for user_archived_address in user_archived_addresses:
                if user_archived_address in ipfs_addresses:
                    ipfs_addresses.remove(user_archived_address)

            # fetch the content details from ipfs
            content_list = []

            for address in ipfs_addresses:
                # fetch content details from ipfs
                content_dict = get_content_from_ipfs(address)

                if len(content_dict['data']) >= 250:
                    clean_text = re.sub('<[^<]+?>', '', content_dict['data'])
                    content_dict['data'] = f"{clean_text[:250]}..."

                content_obj = get_object_or_404(Content, ipfs_address=address)
                content_dict['id'] = content_obj.id
                content_dict['post_time'] = content_obj.created_at

                if content_obj.is_updated:
                    content_dict['updated_time'] = content_obj.updated_at

                content_dict['user'] = request.user

                content_list.append(content_dict)

            context = {
                'content_list': content_list,
                'archived_content': len(content_list)
            }

            return render(request, 'content/archived_content.html', context=context)
        return redirect('wallet')


class ViewDetailedArchivedContent(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        content_id = kwargs.get('content_id')
        post = Content.objects.get(pk=content_id)

        # fetch content details from ipfs
        content_data = get_content_from_ipfs(post.ipfs_address)

        context = {
            'content': content_data,
            'content_creator': request.user,
            'post_time': post.created_at,
            'content_id': content_id
        }

        if post.is_updated:
            context['updated_time'] = post.updated_at

        return render(request, 'content/view_detailed_archived_content.html', context=context)


class TransferSparkTokens(LoginRequiredMixin, View):
    """
    transfer spark tokens from user's account to another user
    """

    def get(self, request):
        return render(request, 'content/transfer_spark_tokens.html', {'title': 'Transfer Spark Tokens'})

    def post(self, request):
        username = request.POST.get('user')

        # if the user with that username exists
        if user_obj := CustomUser.objects.filter(username=username).first():
            if user_obj == request.user:
                messages.warning(request, "You need not transfer tokens to your own account.")
                return redirect('transfer_spark_tokens')

            # if the user has not registered a MetaMask wallet address
            elif not Web3.isAddress(user_obj.wallet_address):
                messages.error(request, "Cannot initiate the transaction. The user has not registered their wallet "
                                        "address with ShareSparks.")
                return redirect('transfer_spark_tokens')

            # transfer the amount
            else:
                token_value_in_spk = float(request.POST.get('tokens'))
                token_value_in_wei = token_value_in_spk * (10 ** 18)
                token_value = int(token_value_in_wei)

                context = {
                    'contract_address': os.environ.get('CONTRACT_ADDRESS'),
                    'from_address': request.user.wallet_address,
                    'to_wallet_address': user_obj.wallet_address,
                    'token_value': token_value
                }
                return render(request, 'content/wait_to_transfer_tokens.html', context=context)

        else:
            messages.error(request, "Sorry! User with that username does not exist. Please enter a valid username.")
            return redirect('transfer_spark_tokens')


class ContentRewardsView(LoginRequiredMixin, View):

    def get(self, request, content_id):
        content_rewards = ContentRewards.objects.filter(content_id=content_id, is_rewarded=True)
        next_rewards = Rewards.objects.exclude(id__in=content_rewards.values('reward_id'))

        context = {
            'content_rewards': content_rewards,
            'next_rewards': next_rewards,
        }

        return render(request, 'content/content_rewards.html', context)


class FilterAccToCategory(LoginRequiredMixin, View):
    def get(self, request, category):
        category_obj = get_object_or_404(ContentCategory, category=category)
        contents = Content.objects.filter(category__category=category, is_archived=False,
                                          user__is_active=True).order_by(
            '-created_at')
        page_number = self.request.GET.get('page')
        context = get_list_of_content(contents, context={}, page_number=page_number)

        context['title'] = category_obj.category

        return render(request, 'content/filter_acc_category_post.html', context=context)


class AddSparkTokensView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'content/add_spark_tokens.html',
                      {'contract_address': os.environ.get('CONTRACT_ADDRESS')})
