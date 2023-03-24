import os

from celery import shared_task
from django.core.mail import EmailMessage
from django.db import IntegrityError
from django.db.models import Count
from django.template.loader import render_to_string
from web3 import Web3

from content.models import Comments, Likes, Rewards, ContentRewards
from content.utils import create_contract_instance, create_web3_instance
from users.models import CustomUser


@shared_task()
def fetch_rewards_content():
    fetch_comment_rewards()
    fetch_like_rewards()


def fetch_comment_rewards():
    comments = Comments.objects.values('content_id').annotate(target_count=Count('content_id')).filter(
        content__is_archived=False)

    filter_eligible_content('comment', comments)


def fetch_like_rewards():
    likes = Likes.objects.values('content_id').annotate(target_count=Count('content_id')).filter(
        content__is_archived=False)

    filter_eligible_content('like', likes)


def filter_eligible_content(target_type, targets):
    rewards = Rewards.objects.filter(target_type=target_type)

    for reward in rewards:
        for target in targets:
            if target['target_count'] >= reward.target:
                try:
                    ContentRewards(content_id=target['content_id'], reward_id=reward.id).save()
                except IntegrityError:
                    pass


def send_mail(email):
    subject = ' Contract Balance Insufficient'
    email_from = 'from@example.com'
    recipient_list = [email]
    message = render_to_string('content/insufficient_balance.html')
    email = EmailMessage(subject, message, email_from, recipient_list)
    email.content_subtype = 'html'
    email.send()


@shared_task()
def give_rewards():
    contents = ContentRewards.objects.filter(is_rewarded=False)
    contract = create_contract_instance()
    w3 = create_web3_instance()
    public_address = os.environ.get('PUBLIC_ADDRESS')
    chain_id = int(os.environ.get('CHAIN_ID'))

    for content in contents:
        address = Web3.toChecksumAddress(content.content.user.wallet_address)
        reward = Web3.toWei(content.reward.token, 'ether')
        contract_balance = contract.functions.balanceOf(os.environ.get('CONTRACT_ADDRESS')).call()
        if reward < contract_balance:
            # build the transaction
            txn = contract.functions.giveReward(address, reward).buildTransaction(
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
                content.is_rewarded = True
                txn_link = txn_receipt['transactionHash'].hex()
                content.transaction_link = txn_link
                content.save()
        else:
            admin_users = CustomUser.objects.filter(is_superuser=True).all()
            email_list = [admin.email for admin in admin_users]
            send_mail(email_list)
            break
