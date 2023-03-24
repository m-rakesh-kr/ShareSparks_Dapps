// get cookie value for post method
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// if the user switched account
window.ethereum.on('accountsChanged', async function () {
    window.location.reload()
})

// if the user switches the network/chain
window.ethereum.on('chainChanged', function (_chainId) {
    window.location.reload()
})