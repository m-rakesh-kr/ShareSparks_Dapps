import hashlib
import os
import io
import json
import re

import ipfshttpclient
from django.core.paginator import Paginator
from django.db.models import Count

from web3 import Web3
from dotenv import load_dotenv

from content.models import Likes, Content, ContentCategory
from users.models import CustomUser

load_dotenv()

counter = 0


def create_web3_instance():
    alchemy_url = os.environ.get('ALCHEMY_URL')
    return Web3(Web3.HTTPProvider(alchemy_url))


def get_contract_abi():
    with open("./contract_abi.json", 'r') as file:
        return file.read()


def create_contract_instance():
    w3 = create_web3_instance()

    abi = get_contract_abi()

    # connect with contract
    contract_address = os.environ.get('CONTRACT_ADDRESS')
    contract = w3.eth.contract(address=contract_address, abi=abi)
    return contract


def create_ipfs_client():
    return ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')


def create_folder_on_ipfs():
    """
    Creates a directory within the MFS (Mutable File System)
    :return: folder hash
    """
    client = create_ipfs_client()

    client.files.mkdir('/ShareSparks', parents=True)
    file_stat = client.files.stat('/ShareSparks')['Hash']

    # use this pin method to pin folder in ipfs
    client.pin.add(file_stat)

    return file_stat


def add_content_on_ipfs(content_data, username, title):
    """
    Use to store json file in given file path
    :param title: title of the content
    :param username: username of the content owner
    :param content_data: the data of the content
    :return: Hash of json file
    """
    global counter

    file_path = f'/ShareSparks/{counter}_{username}_{title}.json'
    counter += 1

    json_data = json.dumps(content_data).encode()

    # add file in the folder
    client = create_ipfs_client()
    client.files.write(file_path, io.BytesIO(json_data), create=True)

    # Use to fetch Hash of file
    file_hash = client.files.stat(file_path)['Hash']
    return file_hash


def get_content_from_ipfs(filehash):
    """
    This method use to get file content using filehash
    :param filehash: Hash of file which you want to fetch
    :return: json data
    """
    client = create_ipfs_client()
    return client.get_json(filehash)


class MyCustomPaginator(Paginator):
    def get_paginated_items(self, page_number, page_size):
        """
        Returns a list of items for the specified page number and size.
        """
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        return self.object_list[start_index:end_index]


def get_list_of_content(content_obj, context, page_number):
    content_list = []
    contract = create_contract_instance()
    for content in content_obj:
        # fetch content details from ipfs
        content_dict = get_content_from_ipfs(content.ipfs_address)

        if len(content_dict['data']) >= 250:
            clean_text = re.sub('<[^<]+?>', '', content_dict['data'])
            content_dict['data'] = f"{clean_text[:250]}..."

        # fetch content creator's address from blockchain
        user_address = contract.functions.getIpfsAuthor(content.ipfs_address).call()
        user_wallet_address = user_address.lower()

        user_obj = CustomUser.objects.get(wallet_address=user_wallet_address)
        content_dict['user'] = user_obj

        content_dict['id'] = content.id
        content_dict['post_time'] = content.created_at

        if content.is_updated:
            content_dict['updated_time'] = content.updated_at

        content_list.append(content_dict)

    paginator = MyCustomPaginator(content_list, 3)  # Display 3 items per page
    page_obj = paginator.get_page(page_number)
    context['posts'] = paginator.get_paginated_items(page_obj.number, page_obj.paginator.per_page)
    context['page_obj'] = page_obj

    top_posts = Likes.objects.values('content__ipfs_address').annotate(target_count=Count('content_id')).filter(
        content__is_archived=False).order_by('-target_count')[:5]

    trending_content = []

    for post in top_posts:
        ipfs_address = post.get('content__ipfs_address')
        ipfs_data = get_content_from_ipfs(ipfs_address)

        content_obj = Content.objects.get(ipfs_address=ipfs_address)
        user_obj = content_obj.user
        ipfs_data['user'] = user_obj
        ipfs_data['content'] = content_obj
        trending_content.append(ipfs_data)

    context['trending_content'] = trending_content

    contents = Content.objects.values('category_id').annotate(content_count=Count('category_id')).filter(
        is_archived=False).order_by('-content_count')[:5]
    context['categories'] = ContentCategory.objects.filter(id__in=contents.values('category_id'))

    return context


# def add_content_to_pinata(content_data, username, title):
#     """
#     to add the json content to IPFS (Pinata)
#     :param content_data: content data to be stored on IPFS in json format
#     :param username: username of the content writer
#     :param title: title of the content
#     :return: IPFS hash address of the data
#     """
#
#     # Pinata API endpoint
#     pinata_url = os.environ.get("PINATA_URL")
#
#     # Pinata API keys
#     headers = {
#         "Content-Type": "application/json",
#         "pinata_api_key": os.environ.get("PINATA_API_KEY"),
#         "pinata_secret_api_key": os.environ.get("PINATA_SECRET_API_KEY")
#     }
#
#     # Convert JSON data to string
#     payload = {
#         'pinataContent': json.dumps(content_data),
#         'pinataMetadata': {
#             'name': f'{username}_{title}'
#         }
#     }
#
#     # Send POST request to Pinata API
#     response = requests.post(pinata_url, headers=headers, json=payload)
#
#     # Parse response data
#     result = response.json()
#
#     # Extract IPFS hash from response
#     return result['IpfsHash']
#
#
# def get_content_from_ipfs(content_address):
#     data = requests.get(f"https://gateway.pinata.cloud/ipfs/{content_address}")
#     print(data.status_code)
#     return data.json() if data.status_code == 200 else 'error'

