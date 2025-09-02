# Chatbot Uptiimum

## Présentation
***Up_AI*** est une intelligence artificielle conçue pour guider les utilisateurs de l'ERP Uptiimum durant leur navigation. Elle aide à comprendre et à utiliser les différents modules de l'application, que sont la gestion des patients, la gestion de la caisse, la gestion du laboratoire, la gestion de la pharmacie et la gestion des ressources humaines.

Il s'agit entre autre d'un Chatbot, une application interactive développée avec Streamlit, conçue pour répondre aux questions des utilisateurs en se basant sur la documentation Markdown de l'ERP Uptiimum. Propulsé par l'API Groq, ce chatbot utilise le modèle LLaMA3-70B pour fournir des réponses précises et contextuelles. Il inclut des fonctionnalités avancées telles que :

- **Interface utilisateur intuitive** : Une interface Streamlit responsive avec un champ de saisie fixe pour poser des questions et un historique des messages défilant.
- **Simulation de réflexion** : Affiche un message "Réflexion de l'IA..." pendant la génération des réponses pour une expérience utilisateur fluide.
- **Synthèse vocale** : Les réponses du bot peuvent être lues à voix haute (en français, vitesse modifiable) grâce à l'intégration de gTTS, avec une icône de haut-parleur cliquable.
- **Sauvegarde des conversations** : Les échanges sont enregistrés dans un fichier JSON et accessibles via une sidebar pour une consultation ultérieure.
- **Documentation locale** : Charge les fichiers Markdown du dossier docs pour fournir des réponses basées uniquement sur la documentation fournie.

Ce projet est idéal pour les entreprises ou les développeurs souhaitant créer un assistant IA spécialisé, capable de répondre aux questions sur une application spécifique en s'appuyant sur une documentation structurée. Le code est modulaire, open-source, et prêt à être déployé sur des plateformes comme Hugging Face Spaces.


## Installation et déploiement :

### Windows
Pour la déployer sur votre PC **windows**, les étapes à suivre sont les suivantes :

- Téléchargez et installez python dans votre PC : de préférence, la version `Python 3.10.11` (très stable par rapport aux plus récentes)

- créez un dossier (Venv) où vous stockerez vos environnements virtuel pour exécuter l'app. Par défaut, installez-le dans le répertoire des documents de la partition principale.

- ouvrez le dossier créé à partir du terminal puis insérez
  ```bash
   pip install virtualenv
  ```

- Une fois l'action éxécutée, créez un environnement virtuel avec le nom de votre choix en tapant la commande :
  ``` bash
  virtualenv mon_env
  ```

- Dès que l'environnement est créé, activez-le avec *``./mon_env/Scripts/activate``* ensuite placez vous dans ce dossier (*cd mon_env*).

- Cloner le projet dans ce dossier là avec la commande `git clone https://github.com/Lemtiel/ProjetBach.git`

- ouvrez le dossier *mon_env* dans votre IDE ; dans le dossier du projet qui a été cloné, il y a la liste des dépendances à télécharger dans le fichier requirement.txt. Dans votre terminal, installez avec la commande : **pip install *mes_dépendances***

- Une fois les dépendances téléchargées, dans votre terminal, éxécutez la commande :


```bash
treamlit run Up_AI-v2.py
```


### Hugging Face

Vous pouvez déployer ce chatbot sur Hugging Face Spaces pour le rendre accessible en ligne via une URL publique, en utilisant des instances CPU gratuites. Voici les étapes pour déployer votre application :

$-> Préréquis$
- Au préalable vous créer un compte sur la plateforme [hugging Face](https://huggingface.co)
- Une clé [API Groq](https://groq.com)
- Votre projet poussé sur un dépôt GitHub public ou privé.

$-> Etapes$
- Connectez-vous à votre compte Hugging Face.
- Accédez à Hugging Face Spaces et cliquez sur Create new Space.
- Nommez votre Space (ex. : mon-chatbot) et choisissez docker > blank-project comme framework.
- Sélectionnez Public ou Private selon vos préférences.

$-> Configurer les fichiers nécessaires :$
- Assurez-vous que votre dépôt GitHub contient :
  - chatbot.py : Le fichier principal de l'application Streamlit.
  - requirements.txt : Liste des dépendances nécessaires :
    ```bash 
    streamlit
    groq
    python-dotenv
    gtts
    ```
  - speaker.png : L'icône de haut-parleur pour la lecture audio (placez une image PNG 24x24 dans le répertoire racine).
  - Dossier docs : Contenant vos fichiers Markdown (ex. : docs/guide.md).

- Poussez ces fichiers sur votre dépôt GitHub :
    ```bash
    git add .
    git commit -m "Préparation pour déploiement sur Hugging Face Spaces"
    git push origin main
    ```
$-> onfigurer la clé API Groq :$
- Dans l'interface de Hugging Face Spaces, allez dans Settings > Secrets.
- Ajoutez une nouvelle variable secrète :
    - Nom : GROQ_API_KEY
    - Valeur : Votre clé API obtenue depuis console.groq.com.
- Enregistrez les modifications.

$-> Déployer l'application :$
- Une fois le dépôt lié, Hugging Face détectera automatiquement chatbot.py et requirements.txt.
- Le Space installera les dépendances et construira l'application. Consultez les Build Logs pour vérifier l'état du déploiement.
- Après un déploiement réussi, accédez à votre application via l'URL fournie

$-> Tester l'application :$
- Ouvrez l'URL du Space dans un navigateur.
- Vérifiez que :
  - Le champ de saisie en bas est accessible pour poser des questions.
  - Les réponses du bot s'affichent dans l'historique avec l'icône speaker.png pour la lecture audio.
  - Les conversations sont sauvegardées dans la sidebar.
- Si des erreurs surviennent, consultez les Build Logs ou App Logs dans Hugging Face Spaces pour diagnostiquer les problèmes.

$-> Conseils pour le déploiement :$
- **Clé API Groq** : Assurez-vous que la clé API est correctement configurée dans les secrets du Space pour éviter l'erreur 401 Invalid API Key.
- **Performance** : Les instances CPU gratuites de Hugging Face sont adaptées aux applications légères. Pour des performances améliorées, envisagez un Space avec une instance GPU payante.
- **Mises à jour** : Toute modification du code sur GitHub déclenchera un redéploiement automatique. Assurez-vous de tester localement avant de pousser les changements :
  
    ```bash
    streamlit run chatbot.py
    ```
    
- **Dépannage** : Si l'application ne se charge pas, vérifiez que speaker.png est accessible (ex. : https://raw.githubusercontent.com/Lemtiel/documentation_Uptiimum/main/speaker.png) et que le dossier docs est inclus dans le dépôt.
