
// the URL and the websocket OBJ has been created in the detail post file instead
//let url = `ws://${window.location.host}/ws/socket-server/${post_user}` // instead of http, we use websocket channel (ws)

//create websocket object
//const notifSocket = new WebSocket(url)

$(document).on('click', document, function(e){

    // the message notif only refers to the channel notification
    // for context there are other message notif in detail post and home template, just named differently
    if (e.target.id === 'message_close'){
        const message_notif = e.target.closest('#message_notif')
        const message_text = message_notif.querySelector('#message_text')

        if (!message_notif.classList.contains('hidden')){
            message_notif.classList.add('hidden')
            message_text.innerHTML = ""
        }
    }
})

// this event will fire when data is received through a websocket or data coming from our backend
notifSocket.onmessage = function(e){
    let data = JSON.parse(e.data)
    console.log('the data: ', data)
    let notif_div = document.getElementById('message_notif')
    let notif_header = document.getElementById('message_header')

    if (data){
        notif_div.classList.remove('hidden')
        if (data.notif_type === 'post_vote'){
            notif_div.querySelector('#message_text').innerHTML = `post: ${data.post_title}`

        } 
        
        else if ( data.notif_type === 'post_comment' || data.notif_type === 'comment_reply'){
            notif_div.querySelector('#message_text').innerHTML = `their comment: ${data.comment_body}`
        }
        else if ( data.notif_type === 'comment_vote'){
            notif_div.querySelector('#message_text').innerHTML = `comment: ${data.comment_body}`
        }
        
        notif_header.innerHTML = data.message
        $('#sender_profile').attr('src', data.img_path)
    }
    
}

notifSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

window.removeEventListener('resize', window)

