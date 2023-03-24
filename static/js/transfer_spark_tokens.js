function transferTokens(contractAddress, fromAddress, toAddress, tokenValue) {
    const web3 = new Web3(Web3.givenProvider)
    fetch("/get-contract-abi").then(
        response => {
            return response.json()
        }
    ).then(async abi => {
        const contract = new web3.eth.Contract(abi, contractAddress);

        await contract.methods.transfer(toAddress, tokenValue).send({
            from: fromAddress
        }).on('transactionHash', function (hash) {
            Swal.fire({
                title: 'Transferring Tokens',
                html: `Your transaction is pending...<br>Please wait till we transfer the tokens.<br>Do not close this page.` +
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
                    html: `Congratulations!!! <br>Your transaction was successful.<br>Your tokens have been transferred.` +
                        `<br>Click <a style="color: #8f5dc3; font-style: italic" href="https://mumbai.polygonscan.com/tx/${receipt.transactionHash}" target="_blank">here</a> to view your transaction`,
                    icon: 'success',
                    iconColor: 'white',
                    confirmButtonText: 'OK',
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    allowEnterKey: false,
                    customClass: 'swal-style'
                }).then(() => {
                    let url = window.location.protocol + '//' + window.location.host + '/wallet/'
                    window.location.assign(url)
                })
            } else {
                Swal.fire({
                    title: 'Transaction Error',
                    html: `Oops! There was some error in completing your transaction.<br>Please transfer the tokens again` +
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
                    text: 'You need to confirm the transaction to transfer the tokens.',
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
                    html: 'Oops! There was some error in your transaction.<br>Please initiate the transaction again',
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