// Déclaration des variables globales pour les connexions WebSocket
let chatSocket = null;
let statusSocket = null;
let commentSocket = null;  // Déclarée en haut, mais initialisée plus tard

// Récupération du nom d'utilisateur actuel depuis le template Django
 //const username = "{{ user.username }}"; // Nom d'utilisateur actuel



//const currentUsername = "{{ request.user.username }}";

// Connexion au WebSocket de statut global
window.addEventListener("load", () => {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  statusSocket = new WebSocket(`${protocol}://${window.location.host}/ws/status/`);

  statusSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.type === 'user-status-update') {
      const userElements = document.querySelectorAll('#user-list > div');

      userElements.forEach(userDiv => {
        const usernameSpan = userDiv.querySelector('span.font-medium');
        const statusDot = userDiv.querySelector('span.absolute');

        if (usernameSpan.innerText === data.username) {
          if (data.status === 'online') {
            statusDot.classList.add('bg-yellow-500');
            statusDot.classList.remove('bg-gray-400');
          } else {
            statusDot.classList.add('bg-gray-400');
            statusDot.classList.remove('bg-yellow-500');
          }
        }
      });
    }
  };
});

// Fonction pour ouvrir le modal des utilisateurs
function openUsersModal() {
  document.getElementById("userModal").classList.remove("hidden");

  // Requête AJAX pour obtenir la liste des utilisateurs
  fetch('/get_all_users/')
    .then(response => response.json())
    .then(data => {
      const userListContainer = document.getElementById('user-list');
      userListContainer.innerHTML = '';

      data.users.forEach(user => {
        const userDiv = document.createElement('div');
        userDiv.classList.add('flex', 'items-center', 'gap-4', 'cursor-pointer', 'hover:bg-gray-100', 'p-2', 'rounded');
        userDiv.addEventListener('click', () => selectUser(user.username, user.picture));

        userDiv.innerHTML = `
          <div class="relative">
            <img src="${user.picture}" class="w-12 h-12 rounded-full object-cover border">
            <span class="absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white ${user.online ? 'bg-yellow-500' : 'bg-gray-400'}"></span>
          </div>
          <span class="font-medium">${user.username}</span>
        `;

        userListContainer.appendChild(userDiv);
      });
    })
    .catch(error => console.error('Erreur lors de la récupération des utilisateurs:', error));
}

// Fonction pour fermer le modal des utilisateurs
function closeUsersModal() {
  document.getElementById("userModal").classList.add("hidden");
}

// Fonction appelée lors de la sélection d'un utilisateur
function selectUser(username, picture) {
  closeUsersModal();
  openChatModal(username, picture);
}

// Fonction pour ouvrir le modal de chat avec un utilisateur spécifique
function openChatModal(username, picture) {
  document.getElementById("chatModal").classList.remove("hidden");
  document.getElementById("chat-header-name").innerText = username;
  document.getElementById("chat-header-pic").src = picture;

  // Fermeture de la précédente connexion WebSocket si elle existe
  if (chatSocket) {
    chatSocket.close();
  }

  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  chatSocket = new WebSocket(`${protocol}://${window.location.host}/ws/chat/${currentUsername}/${username}/`);

  chatSocket.onopen = function() {
    console.log("Connexion WebSocket établie");
  };

  chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const messageContainer = document.getElementById('messageContent');

    if (data.type === 'chat_message') {
      const messageDiv = document.createElement("div");
      const isSender = data.sender === currentUsername;

      messageDiv.classList.add('flex', isSender ? 'justify-end' : 'justify-start', 'gap-4', 'mb-2');
      messageDiv.innerHTML = `
        <div class="${isSender ? 'bg-blue-500 text-white' : 'bg-gray-200 text-black'} p-2 rounded-lg max-w-[80%]">
          ${data.message}
          ${isSender && data.seen ? '<span class="text-green-200 text-sm ml-2">Vu</span>' : ''}
        </div>
      `;
      messageContainer.appendChild(messageDiv);
      messageContainer.scrollTop = messageContainer.scrollHeight;
    } else if (data.type === 'user-status') {
      const statusIcon = document.getElementById('user-status-icon');
      if (data.status === 'online') {
        statusIcon.classList.add('bg-yellow-700');
        statusIcon.classList.remove('bg-gray-700');
      } else {
        statusIcon.classList.add('bg-gray-700');
        statusIcon.classList.remove('bg-yellow-700');
      }
    }
  };

  chatSocket.onerror = function(error) {
    console.error("Erreur WebSocket : ", error);
  };

  chatSocket.onclose = function(event) {
    if (event.wasClean) {
      console.log("Connexion WebSocket fermée proprement");
    } else {
      console.error("Erreur de connexion WebSocket : ", event);
    }
  };
}

// Fonction pour envoyer un message
function sendMessage(event) {
  event.preventDefault();

  const messageInput = document.getElementById("chatInput");
  const errorMessage = document.getElementById("error-message");
  const messageContent = messageInput.value.trim();

  if (messageContent === "") {
    errorMessage.classList.remove("hidden");
    return;
  }

  if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
    chatSocket.send(JSON.stringify({
      'message': messageContent,
      'sender': currentUsername,
      'receiver': document.getElementById("chat-header-name").innerText.trim()
    }));
    messageInput.value = '';
    errorMessage.classList.add("hidden");
  } else {
    console.error("WebSocket non connecté.");
  }
}

// Fonction pour fermer le modal de chat
function closeChatModal() {
  document.getElementById("chatModal").classList.add("hidden");
  if (chatSocket) {
    chatSocket.close();
    chatSocket = null;
  }
}


//Interaction du Dropdown
const profileBtn = document.getElementById('profileBtn');
  const dropdownMenu = document.getElementById('dropdownMenu');

  profileBtn.addEventListener('click', () => {
    dropdownMenu.classList.toggle('hidden');
  });


//Fonction qui filtre les services dans marketplace
  function filterByCategory(category) {
  fetch(`/marketplace/filter/${category}/`)
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById('services-list');
      container.innerHTML = '';
      data.services.forEach(service => {
        container.innerHTML += `
          <div class="bg-white shadow p-4 rounded">
            <h2 class="text-xl font-semibold">${service.title}</h2>
            <p class="text-gray-700">${service.description}</p>
            <p class="text-blue-600 font-bold">${service.price} €</p>
            <p class="text-sm text-gray-500">${service.category}</p>
          </div>
        `;
      });
    });
}

//Fonction qui ouvre les modaux dans publier

function openGameModal() {
  document.getElementById('gameModal').classList.remove('hidden');
}

function closeGameModal() {
  document.getElementById('gameModal').classList.add('hidden');
}

function openClipModal() {
  document.getElementById('clipModal').classList.remove('hidden');
}

function closeClipModal() {
  document.getElementById('clipModal').classList.add('hidden');
}

function openPostModal() {
  document.getElementById('postModal').classList.remove('hidden');
}

function closePostModal() {
  document.getElementById('postModal').classList.add('hidden');
}

//Compter les notifications

function fetchNotificationCount() {
    fetch('/notifications/unread_count/')
    .then(response => response.json())
    .then(data => {
        const countElement = document.getElementById('notification-count');
        if (data.unread_count > 0) {
            countElement.textContent = data.unread_count;
            countElement.classList.remove('hidden');
        } else {
            countElement.classList.add('hidden');
        }
    });
}

// Rafraîchir toutes les 30 secondes (ou moins si tu veux)
setInterval(fetchNotificationCount, 30000);
fetchNotificationCount();  // aussi au chargement de page

//Fonction qui marqur notification comme lu
function markNotificationsRead() {
    fetch('/notifications/mark-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'X-Requested-With': 'XMLHttpRequest'
        }
    }).then(() => {
        document.getElementById('notification-count').textContent = '0';
        document.getElementById('notification-count').classList.add('hidden');
    });
}

function closeNotificationModal() {
    document.getElementById("notificationModal").classList.add("hidden");
  }

function openNotificationModal() {
    const modal = document.getElementById("notificationModal");
    modal.classList.remove("hidden");

    fetch('/load_notifications/')
        .then(response => response.json())
        .then(data => {
            const list = document.getElementById("notification-list");
            list.innerHTML = '';  // Clear previous

            data.notifications.forEach(notification => {
                const notifElem = document.createElement("div");
                notifElem.className = "flex items-center gap-3 hover:bg-gray-100 p-2 rounded cursor-pointer";
                notifElem.onclick = () => {
                    closeNotificationModal();
                    openCommentModal(notification.post_id);
                };

                notifElem.innerHTML = `
                    <img src="${notification.sender_avatar}" class="w-10 h-10 rounded-full border" />
                    <div>
                        <p class="text-sm"><strong>${notification.username}</strong> ${notification.message}</p>
                        <span class="text-xs text-gray-400">${notification.created_at}</span>
                    </div>
                `;
                list.appendChild(notifElem);
            });

            markNotificationsRead();
        });
}


//Incrementation du nombre de nOtification

const notificationSocket = new WebSocket(
  'ws://' + window.location.host + '/ws/notifications/' + userId + '/'
);
notificationSocket.onmessage = function(e) {
  let data = JSON.parse(e.data);

  // 🔔 Crée l’élément de notification
  const notifElem = document.createElement("a");
  notifElem.href = "#";
  notifElem.className = "notification-item flex items-center gap-3 hover:bg-gray-100 p-2 rounded";
  notifElem.dataset.postId = data.post_id;

  notifElem.innerHTML = `
    <img src="${data.sender_avatar}" class="w-10 h-10 rounded-full border" />
    <div>
      <p class="text-sm"><strong>${data.username}</strong> ${data.message}</p>
      <span class="text-xs text-gray-400">${new Date().toLocaleString()}</span>
    </div>
  `;

  //  Ajoute le listener immédiatement
  notifElem.addEventListener('click', function (e) {
    e.preventDefault();
    openPostCommentModal(data.post_id);
  });

  // Ajoute à la liste
  const list = document.getElementById("notification-list");
  list.prepend(notifElem);

  // Ouvre le modal
  document.getElementById("notificationModal").classList.remove("hidden");
};


//Fonction de recommandation
function openRecommendModal() {
  const modal = document.getElementById("recommendModal");
  const content = document.getElementById("recommendContent");
  modal.classList.remove("hidden");

  fetch('/recommend/')
    .then(res => res.text())
    .then(html => {
      content.innerHTML = html;
    })
    .catch(() => {
      content.innerHTML = "<p class='text-red-500'>Erreur de chargement.</p>";
    });
}

function closeRecommendModal() {
  document.getElementById("recommendModal").classList.add("hidden");
}

//PARTIE RESERVER POUR LE  HOME PAGE


  function openCommentModal(postId) {
    console.log("Ouverture du modal");
    document.getElementById("commentModal").classList.remove("hidden");

    // Nouvelle socket (réinitialisée à chaque ouverture de modal)
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    commentSocket = new WebSocket(`${protocol}://${window.location.host}/ws/comments/${postId}/`);

    // Charger les commentaires existants
    fetch(`/load_comments/${postId}/`)
      .then(response => response.json())
      .then(data => {
        const commentList = document.getElementById('comment-list');
        commentList.innerHTML = '';
        data.comments.forEach(comment => {
          const commentElement = document.createElement('div');
          commentElement.classList.add('mb-2', 'flex', 'items-start');
          commentElement.innerHTML = `
            <div class="mr-2">
              <img src="${comment.author_avatar}" class="w-8 h-8 rounded-full" alt="">
            </div>
            <div>
              <p class="text-sm text-gray-700"><strong>${comment.username}</strong> : ${comment.content}</p>
              <span class="text-xs text-gray-500">${comment.created_at}</span>
            </div>
          `;
          commentList.appendChild(commentElement);
        });
      });

    commentSocket.onmessage = function(e) {
      const data = JSON.parse(e.data);
      const commentElement = document.createElement('div');
      commentElement.classList.add('mb-2', 'flex', 'items-start');
      commentElement.innerHTML = `
        <div class="mr-2">
          <img src="${data.author_avatar}" class="w-8 h-8 rounded-full" alt="">
        </div>
        <div>
          <p class="text-sm text-gray-700"><strong>${data.username}</strong> : ${data.comment}</p>
          <span class="text-xs text-gray-500">${data.created_at}</span>
        </div>
      `;
      const list = document.getElementById('comment-list');
      list.appendChild(commentElement);
      list.scrollTop = list.scrollHeight;

      if (data.type === 'new_comment' || data.type === 'history') {
        updateCommentCount(data.comment_count, data.post_id);
      }
    };

    commentSocket.onclose = function(e) {
      console.error('Le socket de commentaire s\'est fermé de manière inattendue');
    };
  }

  function sendComment(e) {
    e.preventDefault();
    const input = document.getElementById("commentInput");
    const comment = input.value.trim();
    if (comment && commentSocket) {
      commentSocket.send(JSON.stringify({
        comment: comment,
        username: username
      }));
      input.value = "";
    }
  }



  // Fonction pour fermer le modal de commentaire
  function closeModal() {
    console.log("Fermeture du modal");
    document.getElementById("commentModal").classList.add("hidden");
  }


//Count le nombre de commentaire
function updateCommentCount(count, postId) {
  const commentCountElem = document.getElementById(`commentCount-${postId}`);
  if (commentCountElem) {
    commentCountElem.textContent = count;
  }
}

//Gestion des likes
//const postId = ...;  // L’ID du post actuel
const likeSocket = new WebSocket(`ws://${window.location.host}/ws/likes/${postId}/`);

likeSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    // Mettre à jour le nombre de likes pour le post
    const likeCountElement = document.getElementById(`like-count-${data.post_id}`);
    if (likeCountElement) {
        likeCountElement.textContent = data.like_count + ' likes';
    }
};

// Fonction pour liker ou unliker un post
function toggleLike(username, action, postId) {
    likeSocket.send(JSON.stringify({
        'action': action,
        'username': username,
        'post_id': postId
    }));
}


function toggleLike(button) {
  const postId = button.dataset.postId;

  fetch(`/like/${postId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(response => response.json())
  .then(data => {
    button.dataset.liked = data.liked;
    button.querySelector('.like-count').textContent = data.like_count;
  })
  .catch(error => console.error('Erreur:', error));
}

function openServiceModal() {
document.getElementById("serviceModal").classList.remove("hidden");
}


function closeServiceModal() {
document.getElementById("serviceModal").classList.add("hidden");
}


function openPGameModal(game_id) {
    fetch(`/play_game/${game_id}/`)
        .then(response => response.text())
        .then(html => {
            document.querySelector("#playGameModal").innerHTML = html;
            document.querySelector("#playGameModal").classList.remove("hidden");
        });
}

function closePlayGameModal() {
    document.querySelector("#playGameModal").classList.add("hidden");
    document.querySelector("#playGameModal").innerHTML = ''; // Vider le contenu pour éviter les conflits
}



