from django.urls import path

from content.views import HomeView, SaveWalletAddressView, VerifyWalletAddress, AddCategoryView, CategoryListView, \
    CategoryUpdateView, CategoryDeleteView, RewardCreateView, RewardsListView, RewardsUpdate, RewardsDelete, \
    UpdatePostFeeView, GetWalletDetailsView, AddContentView, GetContractAbi, AddContentDataInDatabase, LikeView, \
    UnlikeView, ViewDetailedContent, DeleteComment, ViewComments, UpdateContentView, UpdateContentDataInDatabase, \
    ArchiveContentView, GetArchiveContentView, ViewDetailedArchivedContent, TransferSparkTokens, \
    ContentRewardsView, AboutView, FilterAccToCategory, AddSparkTokensView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('save-wallet-address', SaveWalletAddressView.as_view(), name='save_wallet_address'),
    path('verify-wallet-address', VerifyWalletAddress.as_view(), name='verify_wallet_address'),
    path('get-wallet-details', GetWalletDetailsView.as_view(), name='get_wallet_details'),
    path('add-category/', AddCategoryView.as_view(), name='add_category'),
    path('view-categories/', CategoryListView.as_view(), name='view_categories'),
    path('update-category/<int:pk>', CategoryUpdateView.as_view(), name='update_category'),
    path('delete-category/<int:pk>', CategoryDeleteView.as_view(), name='delete_category'),
    path('add-reward/', RewardCreateView.as_view(), name='add_reward'),
    path('view-rewards/', RewardsListView.as_view(), name='view_rewards'),
    path('update-reward/<int:pk>', RewardsUpdate.as_view(), name='update_reward'),
    path('delete-reward/<int:pk>', RewardsDelete.as_view(), name='delete_reward'),
    path('update-post-fee/', UpdatePostFeeView.as_view(), name='update_post_fee'),
    path('add-content/', AddContentView.as_view(), name='add_content'),
    path('add-content-to-database/', AddContentDataInDatabase.as_view(), name='add_content_to_db'),
    path('get-contract-abi', GetContractAbi.as_view(), name='get_contract_abi'),
    path('content/like/<int:content_id>', LikeView.as_view(), name='like'),
    path('content/unlike/<int:content_id>', UnlikeView.as_view(), name='unlike'),
    path('view-detailed-post/<int:content_id>/', ViewDetailedContent.as_view(), name='view_detailed_post'),
    path('delete-comment/<int:pk>', DeleteComment.as_view(), name='delete_comment'),
    path('view-comments/<int:content_id>', ViewComments.as_view(), name='view_comments'),
    path('update-content/<int:content_id>/', UpdateContentView.as_view(), name='update_content'),
    path('update-content-to-database/', UpdateContentDataInDatabase.as_view(), name='update_content_to_db'),
    path('archive-content/<int:content_id>/', ArchiveContentView.as_view(), name='archive_content'),
    path('view-archive-content/', GetArchiveContentView.as_view(), name='view_archive_content'),
    path('view-detailed-archive-content/<int:content_id>/', ViewDetailedArchivedContent.as_view(),
         name='view_detailed_archived_content'),
    path('transfer-spark-tokens/', TransferSparkTokens.as_view(), name='transfer_spark_tokens'),
    path('content-rewards/<int:content_id>/', ContentRewardsView.as_view(), name='content_rewards'),
    path('filter-content/<str:category>/', FilterAccToCategory.as_view(), name='filter-content'),
    path('add-spark-tokens/', AddSparkTokensView.as_view(), name='add_spark_tokens'),
]
