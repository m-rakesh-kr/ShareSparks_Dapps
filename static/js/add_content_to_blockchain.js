function addToBlockchain(ipfsAddress, userAddress, contractAddress, content_id, func,category_id) {
    const web3 = new Web3(Web3.givenProvider)

    const contextData = {
        'ipfs': ipfsAddress,
        'content_id': content_id,
        'category_id':category_id
    }

    fetch("/get-contract-abi").then(
        response => {
            return response.json()
        }
    ).then(async abi => {
        const contract = new web3.eth.Contract(abi, contractAddress);

        // send the data to the blockchain
        await contract.methods.addIpfsHash(ipfsAddress).send({
            from: userAddress,
        }).on('transactionHash', function (hash) {
            Swal.fire({
                title: 'Storing your content on the Blockchain',
                html: `Your transaction is pending...<br>Please wait till we store your content on the blockchain.<br>Do not close this page.` +
                    `<br>Click <a style="color: #8f5dc3; font-style: italic" href="https://mumbai.polygonscan.com/tx/${hash}" target="_blank">here</a> to view your transaction`,
                icon: 'info',
                showConfirmButton: false,
                allowOutsideClick: false,
                allowEscapeKey: false,
                allowEnterKey: false,
                iconColor: 'white',
                customClass: 'swal-style'
            })
        }).on('receipt', function (receipt) {
            if (receipt.status === true) {
                Swal.fire({
                    title: 'Transaction successful',
                    html: `Congratulations!!! <br>Your transaction was successful.<br>Your content has been stored permanently on the blockchain.` +
                        `<br>Click <a style="color: #8f5dc3; font-style: italic" href="https://mumbai.polygonscan.com/tx/${receipt.transactionHash}" target="_blank">here</a> to view your transaction`,
                    icon: 'success',
                    iconColor: 'white',
                    confirmButtonText: 'OK',
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    allowEnterKey: false,
                    customClass: 'swal-style'
                }).then(() => {
                    if (func === 'add') {
                        $.ajax({
                            method: 'POST',
                            url: "/add-content-to-database/",
                            headers: {
                                "X-CSRFToken": getCookie("csrftoken")
                            },
                            data: contextData,
                            success: function (response) {
                                if (response['status'] === 'success') {
                                    window.location.replace('' +
                                        '/')
                                }
                            }
                        })
                    } else {
                        $.ajax({
                            method: 'GET',
                            url: "/update-content-to-database/",
                            data: contextData,
                            success: function (response) {
                                if (response['status'] === 'success') {
                                    window.location.replace('../../')
                                }
                            }
                        })
                    }

                })
            } else {
                Swal.fire({
                    title: 'Transaction Error',
                    html: `Oops! There was some error in completing your transaction.<br>Please submit your content again` +
                        `<br>Click <a style="color: #8f5dc3; font-style: italic" href="https://mumbai.polygonscan.com/tx/${receipt.transactionHash}" target="_blank">here</a> to view your transaction`,
                    icon: 'error',
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    allowEnterKey: false,
                    iconColor: 'white',
                    customClass: 'swal-style'
                }).then(() => {
                    window.history.back()
                })
            }
        }).on('error', function (error) {
            console.log(error)
            if (error.code === 4001) {
                Swal.fire({
                    title: 'Transaction Rejected',
                    text: 'You need to confirm the transaction to post your content.',
                    icon: 'error',
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    allowEnterKey: false,
                    iconColor: 'white',
                    customClass: 'swal-style'
                }).then(() => {
                    window.history.back()
                })
            } else {
                Swal.fire({
                    title: 'Transaction Error',
                    html: 'Oops! There was some error in your transaction.<br>Please submit your content again',
                    icon: 'error',
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    allowEnterKey: false,
                    iconColor: 'beige',
                    customClass: 'swal-style'
                }).then(() => {
                    window.history.back()
                })
            }
        });
    })
}