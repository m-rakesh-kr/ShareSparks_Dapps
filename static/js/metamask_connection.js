async function testConnection(userAddress) {

    let url = window.location.protocol + '//' + window.location.host + '/wallet/'

    if (window.ethereum) {
        const web3 = new Web3(Web3.givenProvider)
        const chainId = await web3.eth.getChainId()

        if (chainId === 80001) {
            let accounts = await web3.eth.getAccounts()
            if (accounts.length !== 0) {
                const account = accounts[0]
                if (account !== userAddress) {
                    window.location.assign(url)
                }
            } else {
                window.location.assign(url)
            }
        } else {
            window.location.assign(url)
        }
    } else {
        window.location.assign(url)
    }
}