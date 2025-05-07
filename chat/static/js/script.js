
// Variable globale pour stocker la connexion WebSocket
let chatSocket = null;

// Fonction pour ouvrir le modal qui affiche la liste des utilisateurs
function openUsersModal() {
  // Affiche le modal en enlevant la classe "hidden"
  document.getElementById("userModal").classList.remove("hidden");

  // Appel AJAX vers la vue Django qui retourne tous les utilisateurs au format JSON
  fetch('/get_all_users/')
    .then(response => response.json()) // Conversion de la réponse en JSON
    .then(data => {
      const userListContainer = document.getElementById('user-list');
      userListContainer.innerHTML = ''; // On vide le conteneur avant d'ajouter la nouvelle liste

      // Pour chaque utilisateur reçu, on crée un bloc cliquable
      data.users.forEach(user => {
        const userDiv = document.createElement('div');
        // Styles Tailwind pour rendre le bloc agréable visuellement
        userDiv.classList.add('flex', 'items-center', 'gap-4', 'cursor-pointer', 'hover:bg-gray-100', 'p-2', 'rounded');
        // Lorsqu'on clique sur un utilisateur, on lance selectUser()
        userDiv.addEventListener('click', () => selectUser(user.username, user.picture));

        // Contenu HTML : image de profil + nom
        userDiv.innerHTML = `
          <img src="${user.picture}" class="w-12 h-12 rounded-full object-cover border">
          <span class="font-medium">${user.username}</span>
        `;

        // Ajoute ce bloc dans la liste
        userListContainer.appendChild(userDiv);
      });
    })
    .catch(error => console.error('Erreur récupération users:', error));
}

// Fonction pour fermer le modal de sélection d'utilisateurs
function closeUsersModal() {
  document.getElementById("userModal").classList.add("hidden");
}

// Fonction appelée quand on sélectionne un utilisateur
function selectUser(username, picture) {
  // Ferme le modal des utilisateurs
  closeUsersModal();

  // Ouvre le modal de chat avec l’utilisateur sélectionné
  openChatModal(username, picture);
}

// Fonction pour ouvrir le modal de chat avec un utilisateur donné
function openChatModal(username, picture) {
  document.getElementById("chatModal").classList.remove("hidden");

  // Affiche l’image et le nom dans l’en-tête du chat
  document.getElementById("chat-header-name").innerText = username;
  document.getElementById("chat-header-pic").src = picture;

  // Récupère le nom d'utilisateur connecté via le template Django
  const currentUsername = "{{ request.user.username }}";

  // Ferme toute ancienne connexion WebSocket ouverte
  if (chatSocket) {
    chatSocket.close();
  }

  // Crée une nouvelle connexion WebSocket dynamique avec l’utilisateur sélectionné


   chatSocket = new WebSocket(`ws://${window.location.host}/ws/artistapp/${currentUsername}/${username}/`);


  //chatSocket = new WebSocket(`ws://${window.location.host}/ws/artistapp/${username}/?sender=${currentUsername}`);
chatSocket.onopen = function() {
    console.log("WebSocket connecté");
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
  // Lorsque le serveur envoie un message
  chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data); // On parse le message reçu en JSON
    const messageContainer = document.getElementById('messageContent');

    // Crée un bloc HTML pour afficher le message
    const messageDiv = document.createElement("div");
    messageDiv.classList.add('flex', 'justify-start', 'gap-4');

    // Si le message est vu, on ajoute un petit indicateur "Vu"
    messageDiv.innerHTML = `
      <div class="bg-gray-200 p-2 rounded-lg max-w-[80%]">
        ${data.message}
        ${data.seen ? '<span class="text-green-500 text-sm ml-2">Vu</span>' : ''}
      </div>
    `;

    // Ajoute le message dans le chat
    messageContainer.appendChild(messageDiv);

    // Scroll automatique vers le bas
    messageContainer.scrollTop = messageContainer.scrollHeight;
  };

  // Récupère l’historique des messages avec l’utilisateur sélectionné
  fetch(`/chat_history/${username}/`)
    .then(response => response.json())
    .then(data => {
      const messagesContainer = document.getElementById('messageContent');
      messagesContainer.innerHTML = ''; // Vide l'historique actuel

      // Pour chaque ancien message, on l’ajoute dans le conteneur
      data.messages.forEach(msg => {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add('flex', 'justify-start', 'gap-4');
        messageDiv.innerHTML = `
          <div class="bg-gray-200 p-2 rounded-lg max-w-[80%]">${msg.message}</div>
        `;
        messagesContainer.appendChild(messageDiv);
      });

      // Scroll en bas de l'historique
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    });
}

// Fonction appelée quand l'utilisateur appuie sur le bouton "Envoyer"
function sendMessage(event) {
  event.preventDefault(); // Empêche le rechargement de la page (comportement par défaut du formulaire)

  const messageInput = document.getElementById("chatInput"); //Input texte
  const errorMessage = document.getElementById("error-message"); //  Message d’erreur
  const messageContent = messageInput.value.trim(); // 🔎 Texte propre sans espace inutile

  // Vérifie si le champ est vide
  if (messageContent === "") {
    errorMessage.classList.remove("hidden"); // Affiche le message d’erreur
    return;
  }

  // Si WebSocket est bien connecté
  if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
    chatSocket.send(JSON.stringify({ 'message': messageContent })); // Envoi du message
    messageInput.value = ''; // Réinitialise le champ
    errorMessage.classList.add("hidden"); // Cache le message d’erreur si visible
  } else {
    console.error("WebSocket non connecté.");
  }
}


// Ferme le modal de chat et la connexion WebSocket
function closeChatModal() {
  document.getElementById("chatModal").classList.add("hidden");
  if (chatSocket) {
    chatSocket.close(); // Ferme la socket
    chatSocket = null;
  }
}


