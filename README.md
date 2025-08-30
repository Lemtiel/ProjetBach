# Chatbot Uptiimum
---

#### ***Up_AI*** est une intelligence artificielle conçue pour guider les utilisateurs de l'ERP Uptiimum durant leur navigation. Elle aide à comprendre et à utiliser les différents modules de l'application, que sont la gestion des patients, la gestion de la caisse, la gestion du laboratoire, la gestion de la pharmacie et la gestion des ressources humaines

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
