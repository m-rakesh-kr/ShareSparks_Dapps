let account = null

$(document).ready(async function () {
        if (window.ethereum) {
            const web3 = new Web3(Web3.givenProvider)
            const chainId = await web3.eth.getChainId()

            if (chainId === "80001" || chainId === 80001) {
                let accounts = await web3.eth.getAccounts()
                account = accounts[0]

                $.ajax({
                    method: 'GET',
                    url: '/verify-wallet-address',
                    success: async function (response) {
                        // if the connected wallet is same as the registered address
                        if (account === response['wallet_address']) {
                            document.getElementById('wallet-details').style.display = 'flex'
                            getWalletDetails()
                        }
                        // if the registered account is null and the wallet extension is connected to some other address
                        else if (response['wallet_address'] === null && account !== undefined) {
                            Swal.fire({
                                title: 'Unable to Connect to MetaMask',
                                html: 'Your MetaMask is already connected to an address.<br> Please disconnect it from ' + 'your wallet to register your address with your account.',
                                icon: 'error',
                                allowOutsideClick: false,
                                allowEscapeKey: false,
                                allowEnterKey: false,
                                iconColor: 'white',
                                customClass: 'swal-style'
                            }).then(() => {
                                setTimeout(() => {
                                    window.location.reload()
                                }, 800)
                            })
                        }
                        // if the registered address is null and no wallet address is connected to the site
                        else if (account === undefined && response['wallet_address'] === null) {
                            document.getElementById('connect-metamask').style.display = 'block'
                        }
                        // if there is a registered address but metamask is not connected
                        else if (response['wallet_address'] !== null && account === undefined) {
                            document.getElementById('connect-metamask').style.display = 'block'
                        } else {
                            document.getElementById('connect-metamask').style.display = 'block'
                            Swal.fire({
                                title: 'Unable to Connect to MetaMask',
                                html: 'Please disconnect another address from your wallet and reconnect with ' + 'your registered account.',
                                icon: 'error',
                                allowOutsideClick: false,
                                allowEscapeKey: false,
                                allowEnterKey: false,
                                iconColor: 'white',
                                customClass: 'swal-style'
                            }).then(() => {
                                setTimeout(() => {
                                    window.location.reload()
                                }, 800)
                            })
                        }
                    }
                })
            } else if (chainId === null) {
                setTimeout(() => {
                    Swal.fire({
                        title: 'Unable to Connect to MetaMask',
                        html: 'You need to connect your MetaMask wallet to use ShareSparks.<br>If the problem ' +
                            'continues, please open your MetaMask extension and from your browser and continue ',
                        icon: 'error',
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        allowEnterKey: false,
                        iconColor: 'white',
                        customClass: 'swal-style'
                    }).then(() => {
                        window.location.reload(true)
                    })
                }, 2000)
            } else {
                Swal.fire({
                    title: 'Unable to Connect',
                    text: 'You need to connect your MetaMask wallet to Polygon Mumbai network to use ShareSparks',
                    icon: 'error',
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    allowEnterKey: false,
                    iconColor: 'white',
                    customClass: 'swal-style'
                }).then(() => {
                    setTimeout(() => {
                        window.location.reload(true)
                    }, 2000)
                })
            }
        } else {
            document.getElementById('metamask-extension-not-installed').style.display = 'block'
        }
    }
)

// connect metamask wallet
async function connectWallet() {
    await ethereum.request({
        method: "eth_requestAccounts"
    }).then((address) => {
        $.ajax({
            method: 'POST',
            url: "/save-wallet-address",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },
            data: {
                'account_address': address[0]
            }
        })
    }).catch((err) => {
        // if the user rejects the connection
        if (err.code === 4001) {
            Swal.fire({
                title: 'Connection Rejected',
                text: 'You need to accept the request to connect your wallet.',
                icon: 'error',
                allowOutsideClick: false,
                allowEscapeKey: false,
                allowEnterKey: false,
                iconColor: 'white',
                customClass: 'swal-style'
            }).then(() => {
                window.location.reload()
            })
        } else if (err.code === -32002) {
            // If this happens, there is already a request pending in the user's wallet, and he has asked for
            // another connection
            Swal.fire({
                title: 'Request Pending',
                html: 'There is already a request pending in your MetaMask wallet.<br>Please accept it.',
                icon: 'info',
                allowOutsideClick: false,
                allowEscapeKey: false,
                allowEnterKey: false,
                iconColor: 'white',
                customClass: 'swal-style'
            })
        } else {
            console.log(err)
            Swal.fire({
                title: 'Connection Error',
                html: 'There was some error in connecting your wallet.<br>Please try again.',
                icon: 'error',
                allowOutsideClick: false,
                allowEscapeKey: false,
                allowEnterKey: false,
                iconColor: 'white',
                customClass: 'swal-style'
            })
        }
    })
}

// get wallet details of the connected account
function getWalletDetails() {
    $.ajax({
        method: 'GET',
        url: '/get-wallet-details',
        success: function (response) {
            document.getElementById('wallet').innerText = 'Connected wallet: ' + response['wallet_address']
            document.getElementById('matic-balance').innerText = 'Matic balance: ' + response['matic_balance']
            document.getElementById('spark-token-balance').innerText = 'Spark token balance: ' + response['spark_balance']
        }
    })
}