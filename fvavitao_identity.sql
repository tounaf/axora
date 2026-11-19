-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Hôte : localhost:3306
-- Généré le : lun. 16 nov. 2026 à 12:01
-- Version du serveur : 10.6.23-MariaDB-cll-lve
-- Version de PHP : 7.4.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `fvavitao_identity`
--

-- --------------------------------------------------------

--
-- Structure de la table `association`
--

CREATE TABLE `association` (
  `id` int(11) NOT NULL,
  `fiangonana_id` int(11) NOT NULL,
  `nom` varchar(255) NOT NULL,
  `description` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `association`
--

INSERT INTO `association` (`id`, `fiangonana_id`, `nom`, `description`) VALUES
(1, 2, 'Sampanana Lehilahy Andranovelona', 'Sampana Lehilahy Andranovelona'),
(2, 2, 'Sampana Vehivavy Andranovelona', 'Sampana Vehivavy Andranovelona'),
(3, 2, 'TANORA FILAMATRA ANDRANOVELONA', 'Tanora Filamatra Fiangonana Andranovelona'),
(4, 6, 'SAMPANA LEHILAHY', NULL),
(5, 6, 'SAMPANA VEHIVAVY', NULL),
(6, 6, 'TANORA LEHILAHY (Zokiny)', NULL),
(7, 6, 'TANORA LEHILAHY (Zandriny)', NULL),
(8, 6, 'TANORA VEHIVAVY (Zokiny)', NULL),
(9, 6, 'TANORA VEHIVAVY (Zandriny)', NULL),
(10, 11, 'SAMPANA LEHILAHY', NULL),
(11, 11, 'SAMPANA VEHIVAVY', NULL),
(12, 11, 'TANORA LEHILAHY (Zandriny)', NULL),
(13, 11, 'TANORA LEHILAHY (Zokiny)', NULL),
(14, 11, 'TANORA VEHIVAVY (Zandriny)', NULL),
(15, 11, 'TANORA VEHIVAVY (Zokiny)', NULL),
(16, 10, 'SAMPANA LEHILAHY', NULL),
(17, 10, 'SAMPANA VEHIVAVY', NULL),
(18, 10, 'TANORA LEHILAHY (Zandriny)', NULL),
(19, 10, 'TANORA LEHILAHY (Zokiny)', NULL),
(20, 10, 'TANORA VEHIVAVY (Zandriny)', NULL),
(21, 10, 'TANORA VEHIVAVY (Zokiny)', NULL),
(22, 2, 'TANORA FILAMATRA ANDRANOVELONA (zandriny)', 'Tanora filamatra zandriny (latsakin\'ny 18 taona)'),
(24, 9, 'SAMPANA LEHILAHY', NULL),
(25, 9, 'SAMPANA VEHIVAVY', NULL),
(26, 9, 'TANORA LEHILAHY (Zandriny)', NULL),
(27, 9, 'TANORA LEHILAHY (Zokiny)', NULL),
(28, 9, 'TANORA VEHIVAVY (Zandriny)', NULL),
(29, 9, 'TANORA VEHIVAVY (Zokiny)', NULL),
(30, 8, 'SAMPANA LEHILAHY', NULL),
(31, 8, 'SAMPANA VEHIVAVY', NULL),
(32, 8, 'TANORA LEHILAHY (Zandriny)', NULL),
(33, 8, 'TANORA LEHILAHY (Zokiny)', NULL),
(34, 8, 'TANORA VEHIVAVY (Zandriny)', NULL),
(35, 8, 'TANORA VEHIVAVY (Zokiny)', NULL),
(36, 7, 'SAMPANA LEHILAHY', NULL),
(37, 7, 'SAMPANA VEHIVAVY', NULL),
(38, 7, 'TANORA LEHILAHY (Zandriny)', NULL),
(39, 7, 'TANORA LEHILAHY (Zokiny)', NULL),
(40, 7, 'TANORA VEHIVAVY (Zandriny)', NULL),
(41, 7, 'TANORA VEHIVAVY (Zokiny)', NULL),
(42, 5, 'SAMPANA LEHILAHY', NULL),
(43, 5, 'SAMPANA VEHIVAVY', NULL),
(44, 5, 'TANORA LEHILAHY (Zandriny)', NULL),
(45, 5, 'TANORA LEHILAHY (Zokiny)', NULL),
(46, 5, 'TANORA VEHIVAVY (Zandriny)', NULL),
(47, 5, 'TANORA VEHIVAVY (Zokiny)', NULL),
(48, 4, 'SAMPANA LEHILAHY', NULL),
(49, 4, 'SAMPANA VEHIVAVY', NULL),
(50, 4, 'TANORA LEHILAHY (Zandriny)', NULL),
(51, 4, 'TANORA LEHILAHY (Zokiny)', NULL),
(52, 4, 'TANORA VEHIVAVY (Zandriny)', NULL),
(53, 4, 'TANORA VEHIVAVY (Zokiny)', NULL);

-- --------------------------------------------------------

--
-- Structure de la table `cotisation`
--

CREATE TABLE `cotisation` (
  `id` int(11) NOT NULL,
  `membre_id` int(11) NOT NULL,
  `fiangonana_id` int(11) DEFAULT NULL,
  `association_id` int(11) DEFAULT NULL,
  `groupe_id` int(11) DEFAULT NULL,
  `enregistre_par_id` int(11) DEFAULT NULL,
  `annee` int(11) NOT NULL,
  `mois` int(11) NOT NULL,
  `tranche` int(11) NOT NULL,
  `montant` decimal(10,2) NOT NULL,
  `paid_at` datetime NOT NULL COMMENT '(DC2Type:datetime_immutable)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `cotisation`
--

INSERT INTO `cotisation` (`id`, `membre_id`, `fiangonana_id`, `association_id`, `groupe_id`, `enregistre_par_id`, `annee`, `mois`, `tranche`, `montant`, `paid_at`) VALUES
(1, 166, NULL, 3, NULL, 1, 2026, 1, 1, 2000.00, '2026-09-15 14:50:39'),
(2, 166, NULL, 3, NULL, 1, 2026, 2, 1, 2000.00, '2026-09-15 14:50:58'),
(3, 166, NULL, 3, NULL, 1, 2026, 3, 1, 2000.00, '2026-09-15 14:51:14'),
(4, 166, NULL, 3, NULL, 1, 2026, 4, 1, 2000.00, '2026-09-15 14:51:34'),
(5, 166, NULL, 3, NULL, 1, 2026, 5, 1, 2000.00, '2026-09-15 14:51:48'),
(6, 166, NULL, 3, NULL, 1, 2026, 6, 1, 2000.00, '2026-09-15 14:52:04'),
(7, 166, NULL, 3, NULL, 1, 2026, 7, 1, 2000.00, '2026-09-15 14:52:17'),
(8, 166, NULL, 3, NULL, 1, 2026, 8, 1, 2000.00, '2026-09-15 14:52:30'),
(9, 166, NULL, 3, NULL, 1, 2026, 9, 1, 2000.00, '2026-09-15 14:52:41'),
(10, 166, NULL, 3, NULL, 1, 2026, 10, 1, 2000.00, '2026-09-15 14:52:53'),
(11, 166, NULL, 3, NULL, 1, 2026, 11, 1, 2000.00, '2026-09-15 14:53:06'),
(12, 166, NULL, 3, NULL, 1, 2026, 12, 1, 2000.00, '2026-09-15 14:53:19');

-- --------------------------------------------------------

--
-- Structure de la table `don`
--

CREATE TABLE `don` (
  `id` int(11) NOT NULL,
  `membre_id` int(11) NOT NULL,
  `fiangonana_id` int(11) DEFAULT NULL,
  `association_id` int(11) DEFAULT NULL,
  `groupe_id` int(11) DEFAULT NULL,
  `enregistre_par_id` int(11) DEFAULT NULL,
  `montant` decimal(10,2) NOT NULL,
  `libelle` varchar(255) DEFAULT NULL,
  `paid_at` datetime NOT NULL COMMENT '(DC2Type:datetime_immutable)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `evenement`
--

CREATE TABLE `evenement` (
  `id` int(11) NOT NULL,
  `type_evenement_id` int(11) DEFAULT NULL,
  `fiangonana_id` int(11) DEFAULT NULL,
  `groupe_id` int(11) DEFAULT NULL,
  `association_id` int(11) DEFAULT NULL,
  `nom` varchar(255) NOT NULL,
  `description` longtext DEFAULT NULL,
  `compte_rendu` longtext DEFAULT NULL,
  `date_debut` datetime DEFAULT NULL,
  `date_fin` datetime DEFAULT NULL,
  `lieu` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL COMMENT '(DC2Type:datetime_immutable)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `evenement`
--

INSERT INTO `evenement` (`id`, `type_evenement_id`, `fiangonana_id`, `groupe_id`, `association_id`, `nom`, `description`, `compte_rendu`, `date_debut`, `date_fin`, `lieu`, `created_at`) VALUES
(1, 1, 2, NULL, 3, 'Formation projet digital', NULL, NULL, '2026-08-30 10:31:00', '2026-08-30 12:31:00', 'Ankaraobato', '2026-08-30 11:31:29'),
(2, NULL, 2, 2, NULL, 'vavaka iraisana', NULL, NULL, '2026-09-09 14:00:00', '2026-09-09 22:20:00', 'anranovelona', '2026-09-09 22:21:08'),
(3, NULL, NULL, NULL, 1, 'Fitaomana entana le 15 Septembre 2026', NULL, 'Tena nahafinaritra sy nahafapo tanteraka satria maro ny Rahalahy Tonga nifanome tanana nandritra ny fotoana nibatana fitaoavana , niainga AVY tany Andranovelona ka hatramin\'ny fampidinana izany tany Andranomena. \nNy godrogodro sy jus nokarakarain\'ny Komity koa moa tena nanome Hery noentina niasa\nNa dia tsy nisy café aza dia tena nahavoky tokoa Sady mamy tsara.', '2026-09-15 09:49:00', NULL, 'Andranovelona', '2026-09-15 09:49:52'),
(4, NULL, NULL, NULL, 1, 'Fiambenana Fiara sy Moto à 13h-15h', 'Solontena 2 personnes par groupe', NULL, '2026-09-16 15:00:00', NULL, 'Andranomena', '2026-09-15 17:29:49'),
(5, NULL, NULL, NULL, 1, 'Faangonana fitaovana avy eny andranomena ho taomina alakamisy 17Septembre 2026', 'Lehilahy mavitrika', NULL, '2026-09-16 17:30:00', NULL, 'Andranomena', '2026-09-15 17:32:22'),
(6, NULL, NULL, NULL, 1, 'Fanangonana entana 16 Septembre', 'Fanangonana fitaovana ho eny andranovelona', NULL, '2026-09-16 17:50:00', NULL, 'Andranomena', '2026-09-16 17:32:37'),
(7, NULL, NULL, NULL, 3, 'Fiofanan’ny tanora zokiny', 'Tanora arampahy', NULL, '2026-09-20 09:10:00', NULL, 'Andranovelona', '2026-09-21 23:15:16'),
(8, 1, 4, NULL, 53, 'TANORA SY NY FITIAVANA 18-10-2026', NULL, NULL, '2026-10-18 09:30:00', '2026-10-18 12:05:00', 'Andranovelona', '2026-10-18 10:43:20'),
(9, NULL, NULL, NULL, 3, 'Fiofanana Tanora zandriny (08-11-2026)', 'Fiofanana Tanora zandriny', NULL, '2026-11-08 09:00:00', NULL, 'Ampiangonana', '2026-11-08 08:56:29'),
(10, NULL, NULL, NULL, 3, 'Fiofanana Tanora zokiny', 'Tanora zokiny 15_11_2026', NULL, '2026-11-15 09:00:00', NULL, 'Ampiangonana', '2026-11-15 08:49:21');

-- --------------------------------------------------------

--
-- Structure de la table `evenement_note`
--

CREATE TABLE `evenement_note` (
  `evenement_id` int(11) NOT NULL,
  `note_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `evenement_note`
--

INSERT INTO `evenement_note` (`evenement_id`, `note_id`) VALUES
(3, 1),
(3, 2);

-- --------------------------------------------------------

--
-- Structure de la table `feature`
--

CREATE TABLE `feature` (
  `id` int(11) NOT NULL,
  `code` varchar(100) NOT NULL,
  `label` varchar(255) NOT NULL,
  `category` varchar(50) DEFAULT NULL,
  `description` longtext DEFAULT NULL,
  `target_route` varchar(255) DEFAULT NULL,
  `icon` varchar(100) DEFAULT NULL,
  `sort_order` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `feature`
--

INSERT INTO `feature` (`id`, `code`, `label`, `category`, `description`, `target_route`, `icon`, `sort_order`) VALUES
(1, 'ADMIN_MENU_DASHBOARD', 'Tableau de bord', 'ADMIN_MENU', 'Vue globale de l\'administration et statistiques', 'admin_dashboard', 'fa-solid fa-chart-pie', 10),
(2, 'ADMIN_MENU_FIANGONANA', 'Paroisses (Fiangonana)', 'ADMIN_MENU', 'Gestion des paroisses et de la hiérarchie locale', 'admin_fiangonana_index', 'fa-solid fa-church', 20),
(3, 'ADMIN_MENU_GROUPES', 'Zones (Groupes)', 'ADMIN_MENU', 'Gestion des zones géographiques et groupes', 'admin_groupe_index', 'fa-solid fa-map-location-dot', 30),
(4, 'ADMIN_MENU_ASSOCIATIONS', 'Associations', 'ADMIN_MENU', 'Gestion des associations de la paroisse', 'admin_association_index', 'fa-solid fa-people-group', 40),
(5, 'ADMIN_MENU_TYPES_EVENEMENT', 'Types d\'Événements', 'ADMIN_MENU', 'Catégorisation des événements (Culte, Réunion...)', 'admin_type_evenement_index', 'fa-solid fa-tags', 50),
(6, 'ADMIN_MENU_ROLES', 'Rôles & Sécurité', 'ADMIN_MENU', 'Gestion des rôles, permissions et habilitations CRBAC', 'admin_role_index', 'fa-solid fa-user-shield', 60),
(7, 'ADMIN_MENU_MEMBRES', 'Membres', 'ADMIN_MENU', 'Gestion de l\'annuaire général des membres', 'admin_membre_index', 'fa-solid fa-users', 70),
(8, 'ADMIN_MENU_PRESENCES', 'Présences & Scans', 'ADMIN_MENU', 'Suivi du pointage et historiques des présences', 'admin_presences', 'fa-solid fa-qrcode', 80),
(9, 'MEMBER_PROFILE_VIEW', 'Profil Membre', 'MEMBER_SPACE', 'Consultation des informations personnelles et carte', '/espace-membre/profile', 'fa-solid fa-user', 100),
(10, 'MEMBER_PROFILE_UPDATE', 'Mise à jour Profil', 'MEMBER_SPACE', 'Modification de la fiche et avatar du membre', '/api/membres/{id}/update-profile', 'fa-solid fa-user-pen', 110),
(11, 'MEMBER_PASSWORD_CHANGE', 'Changement Mot de passe', 'MEMBER_SPACE', 'Modification sécurisée du mot de passe', '/api/me/change-password', 'fa-solid fa-key', 120),
(12, 'MEMBER_CARTE_GENERATE', 'Carte de Membre & QR Code', 'MEMBER_SPACE', 'Génération et impression de la carte officielle avec QR Code', '/api/membres/{id}/carte', 'fa-solid fa-id-card', 130),
(13, 'MEMBER_EVENTS_VIEW', 'Liste des Événements', 'MEMBER_SPACE', 'Consultation de l\'agenda et liste des événements', '/espace-membre/events', 'fa-solid fa-calendar-days', 140),
(14, 'MEMBER_EVENT_CREATE', 'Création d\'Événement', 'MEMBER_SPACE', 'Saisie et planification d\'un nouvel événement', '/api/member-events/create', 'fa-solid fa-calendar-plus', 150),
(15, 'MEMBER_EVENT_SCAN', 'Scanner QR Code Présence', 'MEMBER_SPACE', 'Scan caméra direct pour valider la présence lors d\'un événement', '/api/member-events/{id}/scan', 'fa-solid fa-camera-retro', 160),
(16, 'MEMBER_EVENT_ATTENDEES', 'Liste des Présents', 'MEMBER_SPACE', 'Consultation des membres pointés présents à un événement', '/api/member-events/{id}/attendees', 'fa-solid fa-clipboard-user', 170),
(17, 'MEMBER_EVENT_NOTE_ADD', 'Ajouter une Note/Évaluation', 'MEMBER_SPACE', 'Ajout de remarques ou notes sur un événement', '/api/member-events/{id}/add-note', 'fa-solid fa-note-sticky', 180),
(18, 'MEMBER_EVENT_COMPTE_RENDU', 'Compte Rendu Événement', 'MEMBER_SPACE', 'Rédaction du compte rendu ou résumé d\'un événement', '/api/member-events/{id}/compte-rendu', 'fa-solid fa-file-lines', 190),
(19, 'MEMBER_EVENT_MEDIA_UPLOAD', 'Envoi Photos & Vidéos', 'MEMBER_SPACE', 'Téléversement de médias sur un événement', '/api/member-events/{id}/upload-media', 'fa-solid fa-photo-film', 200),
(20, 'MEMBER_AFFILIATIONS_VIEW', 'Mes Affiliations & Groupes', 'MEMBER_SPACE', 'Consultation des affiliations aux associations et zones', '/espace-membre/affiliations', 'fa-solid fa-sitemap', 210),
(21, 'MEMBER_AFFILIATION_MANAGE', 'Gestion Membres Association', 'MEMBER_SPACE', 'Gestion des membres affiliés à son association', '/api/association-membres/save', 'fa-solid fa-user-plus', 220),
(22, 'MEMBER_STATS_VIEW', 'Statistiques de Participation', 'MEMBER_SPACE', 'Consultation du taux d\'assiduité et présence', '/api/membres/{id}/participation-stats', 'fa-solid fa-chart-line', 230);

-- --------------------------------------------------------

--
-- Structure de la table `fiangonana`
--

CREATE TABLE `fiangonana` (
  `id` int(11) NOT NULL,
  `nom` varchar(255) NOT NULL,
  `code` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `fiangonana`
--

INSERT INTO `fiangonana` (`id`, `nom`, `code`) VALUES
(2, 'Andranovelona', 'AndrVL_0001'),
(4, 'NOSIBE', 'NOSB_'),
(5, 'IVATO', 'IVT_'),
(6, 'MORARANO', 'MRRN_'),
(7, 'ANALAMAHITSY', 'ANLMts_'),
(8, 'SABOTSINAMEHANA', 'SAB-NAM_'),
(9, 'ANDRANOMENA', 'ANDRMN_'),
(10, 'ISAINGY', 'ISG_'),
(11, 'TSARAHONENANA', 'TSRNN_');

-- --------------------------------------------------------

--
-- Structure de la table `groupe`
--

CREATE TABLE `groupe` (
  `id` int(11) NOT NULL,
  `fiangonana_id` int(11) NOT NULL,
  `nom` varchar(255) NOT NULL,
  `description` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `groupe`
--

INSERT INTO `groupe` (`id`, `fiangonana_id`, `nom`, `description`) VALUES
(1, 2, 'Groupe Ifarihy', 'Groupe Ifarihy'),
(2, 2, 'Groupe Andranovelona', 'Groupe Andranovelona'),
(3, 2, 'Groupe Ankaraobato', 'Groupe Ankaraobato__VOAFIDY'),
(4, 2, 'Groupe Andoharanofotsy', 'Groupe Andoharanofotsy'),
(5, 2, 'Groupe Anjomakely', 'Groupe Anjomakely'),
(6, 2, 'Groupe Analamanga miray', 'Groupe Analamanga miray');

-- --------------------------------------------------------

--
-- Structure de la table `media`
--

CREATE TABLE `media` (
  `id` int(11) NOT NULL,
  `evenement_id` int(11) DEFAULT NULL,
  `url` varchar(255) NOT NULL,
  `type` varchar(50) NOT NULL,
  `created_at` datetime NOT NULL COMMENT '(DC2Type:datetime_immutable)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `membre`
--

CREATE TABLE `membre` (
  `id` int(11) NOT NULL,
  `zone_geographique_id` int(11) DEFAULT NULL,
  `fiangonana_id` int(11) NOT NULL,
  `nom` varchar(255) NOT NULL,
  `prenom` varchar(255) NOT NULL,
  `email` varchar(180) NOT NULL,
  `telephone` varchar(50) DEFAULT NULL,
  `adresse` varchar(255) DEFAULT NULL,
  `date_naissance` datetime DEFAULT NULL,
  `photo_url` varchar(500) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `roles` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '(DC2Type:json)' CHECK (json_valid(`roles`)),
  `qr_code_token` varchar(255) DEFAULT NULL,
  `sexe` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `membre`
--

INSERT INTO `membre` (`id`, `zone_geographique_id`, `fiangonana_id`, `nom`, `prenom`, `email`, `telephone`, `adresse`, `date_naissance`, `photo_url`, `password`, `roles`, `qr_code_token`, `sexe`) VALUES
(1, 1, 2, 'Fetraharinatovo', 'Nambinina Gilbert', 'harinjatovo.fetra@gmail.com', '0340030261', 'Ankaraobato', '1992-09-19 00:00:00', '/uploads/membres/profile_1_6a93e615856df.jpg', '$2y$13$CtZgaE0vQRP2Ofo.zelT3eReuDeqKCey5kMVUomcLdsIzdE.1ZIfK', '[\"ROLE_USER\",\"ROLE_ADMIN\"]', '33d1504188150d58d56b5efa92ac327d', 'M'),
(2, 1, 2, 'ANDRIAMASINAVALONA', 'Ravolalaina Kezia', 'sombiniainakezia@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'b666ee32e009ceb4e1c3e0cdaa6a496e', 'F'),
(3, 3, 2, 'FANOMEZANTSOA', 'Jean Kelly Isaia', 'fanomezantsoaishai@gmail.com', '0384418211', NULL, '1999-10-10 00:00:00', '/uploads/membres/profile_3_6a9ec3fe82294.jpg', '$2y$13$kCmduT31BQsucDgJn/XSgOOAKFhztZmpZJ4gNo9kFY071d7ppu1eK', '[\"ROLE_USER\"]', 'ec06dad1150ae84f9a9bab3295bb9442', 'M'),
(4, 1, 2, 'Tahianjanahary', 'Fifaliana', 'fifaliana@gmail.com', '0341120654', NULL, NULL, '/uploads/membres/assoc_membre_6a93ee406a11d.jpg', NULL, '[\"ROLE_USER\"]', NULL, NULL),
(5, 2, 2, 'HERINIRINA', 'Manoa Fahatokiana', 'manoa.@gmail.com', '0348551358', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '481310f31c86e82de91c8066b1f53b79', NULL),
(6, 2, 2, 'FANOMEZANTSOA', 'Jean Fetra', 'fetra@gmail.com', '0329127079', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '9c9ba887579dd23bf37195d66abe1c04', NULL),
(7, 2, 2, 'ANDRIANANTENAINA', 'Alain Patrick', 'patrick@gmail.com', '0383470213', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'dc038fd6d28302fc2036082d5ef852a7', NULL),
(8, 2, 2, 'RANDRIANTSILAVINA', 'Abdallah Jean Claude', 'abdallah@gmail.com', '0345219999', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '27265ae634c0c1fc95fad7af79e03385', NULL),
(9, 2, 2, 'RAKOTOBE', 'Charlie', 'charlie@gmail.com', '0326234582', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', NULL, NULL),
(10, 2, 2, 'HERINIRINA', 'Lanja Fandresena', 'lanja@gmail.com', '0345188449', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', NULL, NULL),
(11, 2, 2, 'RANDRIAMAHANDRY', 'Tahiry', 'tahiry@gmail.com', '0383899416', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', NULL, NULL),
(12, 2, 2, 'RAKOTOMAHEFA', 'Alain', 'alain@gmail.com', '0345579865', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '8b7b926b98e7b1d2cd51d5d907f51327', NULL),
(13, 2, 2, 'RANDRIAMAMY', 'Tahiry2', 'tahiry2@gmail.com', '0348110337', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '24c86f0e1c2149a683354a8b2dd95332', NULL),
(14, 2, 2, 'RAMAMONJISOA', 'Yvon', 'yvon@gmail.com', '0388359738', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '73a79bdeb0fc32144e7f5da93687842f', NULL),
(15, 2, 2, 'RAFALIMANANA', 'Ferdinand', 'ferdinad@gmail.com', '0385088491', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'ad15858fb8d54cf5b4937120118ccf62', NULL),
(16, 2, 2, 'RATANDRANIAINA', 'Dominique Edmond', 'edmond@gmil.com', '0387146570', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '24cece596a6a65ab97b0df4c508578d0', NULL),
(17, 2, 2, 'RANDRIAMANANJARA', 'Enol Tonny', 'erol@gmail.com', '0349228909', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'cc33df9e620bd6f57c75c7c664fb151f', NULL),
(18, 2, 2, 'RAMAMONJISOA', 'Heriniaina Miantsa', 'ramamonjisoaheriniaina1803@gmail.com', '0388235047', NULL, '2003-07-18 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', 'bee4059b8ef49657c45b8469fd69c37d', 'M'),
(19, 2, 2, 'RANDRIAMAPIONONA', 'Clément', 'clement@gmail.com', '0377306463', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'e974b62ee8475a51bddeac313b4ca7b7', NULL),
(20, 5, 2, 'RATOJONIRINA', 'Jean Michel', 'jean@gmail.com', '0382535647', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '92d9d12a5b299de16ea3756214256b00', NULL),
(24, 5, 2, 'RANDRIANASOLO', 'Joseph', 'joseph@gmail.com', '0331956726', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '5e1fcf1e8d7fb61aa9f306dbcf92f1d9', NULL),
(25, 5, 2, 'RAKOTOVAONIRINA', 'Tojosoa Jean Michel', 'tojosoa@gmail.com', '0349306270', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '6cce94c34f09569caf1762534b6030b1', NULL),
(26, 5, 2, 'RABEZAKARIMANANA', 'Jonah', 'jonah@gmail.com', '0386089456', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '75708d2db9727e607dc3e8a6e3566542', NULL),
(27, 5, 2, 'RANDRIATSIORINDRAY', 'Olivier', 'olivier@gmail.com', '0344871862', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '578fee61dca3487baf540a1d36599e95', NULL),
(28, 5, 2, 'RASIMEONE', 'Polone', 'polone@gmail.com', '0343059500', NULL, '2007-07-09 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', '6a525db869ad12a536b898347b60a0c7', 'M'),
(35, 5, 2, 'RABEMANANTSOA', 'Justin', 'justin@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '1ed19c15c0d2b87093061fc89d17412d', NULL),
(36, 5, 2, 'RANDRIAMANDIMBY', 'Edmond', 'randria@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '4f1c322b6230cf396fd9091a76c32501', NULL),
(37, 5, 2, 'RAKOTOARISOA', 'Vahatriniaina Ravo', 'ravo@gmail.com', '0341502240', NULL, '2005-03-16 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', '8e63ba4dacfe27eb7fdf212c58ab579a', 'M'),
(38, 5, 2, 'NIRINA', 'Jean Thomas', 'thomas@gmail.com', '0386610182', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'c7ad48e4f1b2cce191b9ea84f4603e6e', NULL),
(39, 5, 2, 'RAKOTOARISOA', 'Sitraka', 'sitraka@gmail.com', '0344300890', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '7c8c9c624493a3209ee89da7c3ccb1d6', NULL),
(40, 5, 2, 'VESTE', 'veste', 'veste@gmail.com', '0382158351', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '3a83c76c312dc9f2ee7591ec58e2bc29', NULL),
(41, 5, 2, 'RAKOTONIAINA', 'Santatra', 'santatra@gmail.com', '0349329139', NULL, '2001-12-11 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', '028af4e27b5207730f508582415f2df2', 'M'),
(42, 5, 2, 'RAKOTONDRAFARA', 'Sevenie', 'sevenie@gmail.com', '0385385091', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'bcd5e9f3d67580ed15f30f4bb360a17f', NULL),
(43, 5, 2, 'RASANTATRINIAINA', 'Herizo', 'herizo@gmail.com', '0385536787', NULL, '1994-09-21 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', '875c352a0e79cba89b999bc6d4a67454', 'M'),
(44, 5, 2, 'ANDRIAMPANDOA', 'Rachel sousah', 'sousah@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '11eccf2ddce408224ce874344612415e', NULL),
(45, 5, 2, 'RANDRIANASOLO', 'Fitahina', 'fitahiana@gmail.com', '0387745298', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'f556143c09cbb378a46a2282a762e115', NULL),
(46, 1, 2, 'RAZAFINDRAVELO', 'Rasoloniaina', 'rasoloniaina@gmail.com', '0341176957', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '40967bac0339817c820e44b72fc57360', NULL),
(47, 1, 2, 'RANDRIANARISOA', 'Oniaiana Jean Jacque', 'jacque@gmail.com', '0340470394', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '62791928d564f7c639b76cc4352b7736', NULL),
(48, 1, 2, 'RAZAFINDRAMANANA', 'Jean Valery Antsasoa', 'antsasoa@gmail.com', '0342450696', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', NULL, NULL),
(71, 1, 2, 'RATSIAMBAZAFY', 'Tahianjanahary Fifaliana', 'ratsimba@gmail.com', '0341092811', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'dfc553483b138d6b72e14b9f040ed810', NULL),
(73, 1, 2, 'RANDRIANARIMALALA', 'George Alain', 'george@gmail.com', '0383617333', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '17cf4296cb6455b8036413ecabf6de6a', NULL),
(74, 1, 2, 'NOMENJANAHARY', 'Joseph Telly', 'telly@gmail.com', '0381456580', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '154167fcff39630ba941480506d14815', NULL),
(75, 1, 2, 'RAHANDRINIRINA', 'Fenoniaina Fanomezantsoa', 'fanomezantsoa@gmail.com', '0386921093', NULL, '2006-12-16 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', 'fc622d22d85470c5ee70f3d001bfe346', 'F'),
(76, 1, 2, 'RAZAFIMAHATRATRA', 'Andrianaina Gilbert', 'gilbert@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '4b59fed196f860cfc7b5323293fba3a2', NULL),
(77, 1, 2, 'RAKOATOMAMONJY', 'Jean Felix', 'felix@gmail.com', '0349006415', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '7a19575068dff74e5e1e4faf704cf2f1', NULL),
(78, 1, 2, 'CHARLES', 'Clément Séverin', 'severin@gmail.com', '0385905038', NULL, '1992-12-28 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', '42006535886aae8a91bd6932011d8003', 'M'),
(79, 1, 2, 'RAHANDRINIRINA', 'Rivoarisoa', 'rivoarisoa@gmail.com', '0345337043', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'ad8408aa7519c8e52d02ac160fd95c60', NULL),
(80, 1, 2, 'RAKOTOARIVONJY', 'Mirindra Félicien', 'mirindra@gmail.com', '0387637948', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '253bde161975d43c541c906fa00dc688', NULL),
(85, 1, 2, 'FETRANIRINA', 'Justin', 'nirina@gmail.com', '0347544590', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'f0c45127ab97e45c243dc524c3f1df14', NULL),
(86, 1, 2, 'MBAHOAKA', 'Jean Baptiste', 'baptiste@gmail.com', '0341988495', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '1e9d7563602bba1d6a3e3d29c6151ce1', NULL),
(87, 1, 2, 'RANDRIAMANJATO', 'Roger', 'roger@gmail.com', '0342074547', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'fa33a90f3fe328d6054c8a49f5cc147f', NULL),
(88, 1, 2, 'MAROJAONA', 'Rollio André', 'rollio@gmail.com', '0343703454', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'ef5db8f76c44cb47bcdbcb28de68fa0c', NULL),
(89, 1, 2, 'RAFETISON', 'Rindra Anadraimampionona', 'rindra@gmail.com', '0349343710', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'be011fb2ff65af23a551a037a61489a7', NULL),
(90, 1, 2, 'RAZAFINDRAKOTO', 'Haritiana Angelo', 'haritiana@gmail.com', '0345131414', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '23757a0a91464e40445726609589cffb', NULL),
(91, 1, 2, 'RAFAMANTASOA', 'Solomampionona Heriniaina', 'solo@gmail.com', '0327676612', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'fe4e051c10054abdb64b27bd6abf95ab', NULL),
(92, 1, 2, 'RAKOTOARIJAONA', 'Jean Baptiste', 'rija@gmail.com', '0383688671', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', NULL, NULL),
(94, 1, 2, 'RAKOTOARIJAONA', 'Jean Baptiste', 'arijaona@gmail.com', '0383688671', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '471d0cebe9e379f5bb9cc70a7b1183fa', NULL),
(95, 1, 2, 'ANDRIAMANAHIRANA', 'Jean Eric', 'eric@gmail.com', '0348318544', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'b2e2098bfbdbc9ba4b064bf0cd70d8c4', NULL),
(96, 1, 2, 'RAKOTONIRINA', 'Honoré', 'honore@gmail.com', '0332911714', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '848743da31ac1ec1c4fc955b2e186e5f', NULL),
(97, 1, 2, 'RAKOTOARIJAONA', 'Andrianony Naina', 'naina@gmail.com', '0348451327', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'b9dc03e650a876fa7e1de185420fc8f8', NULL),
(98, 4, 2, 'RINDRANIAINA', 'Miaritiana', 'miaritiana@gmail.com', '0344896805', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '2ef5cbf0e372d0d67880a0b4f6074a52', NULL),
(99, 4, 2, 'RAKOTOMALALA', 'Dieu Donné', 'donne@gmail.com', '0342939403', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'b1337f91a5524ee4adf92ceb3fa5c20a', NULL),
(100, 4, 2, 'RANDRIANAINA', 'Arnaud', 'arnaud@gmail.com', '0347033409', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '7f4273ce879266543fbc7129cd03ca3a', NULL),
(101, 4, 2, 'RANDRIAMIHAJA', 'Julien', 'julien@gmail.com', '0384853325', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '821d6cde4541024c65ccd833f956cc28', NULL),
(102, 4, 2, 'RANDRIANAIVO', 'Bearisoa', 'bearisoa@gamail.com', '0340738529', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '1850ca217472925ab3e6df4bcb30aae1', NULL),
(103, 4, 2, 'RANENANDRASANANIRINASOA', 'Ralphe', 'ralphe@gmail.com', '0383465102', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'f88b4e37daf4cc2adb9eaa0cfd65ab8f', NULL),
(104, 4, 2, 'LAHY', 'Jean Marie', 'marie@gmail.com', '0339647912', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '3dc1baec5d74db15496dc786c525bb5b', NULL),
(105, 4, 2, 'RAFENOMANANTSOA', 'Norbert', 'norbert@gmail.com', '0333067310', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '3c0c80d5f2e8c0c62f4969a1663d5e80', NULL),
(107, 4, 2, 'RAKOTONDRASOA', 'gilbert', 'rakotondrasoa@gmail.com', '0387853448', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'bbfff18a8dcbfb744a35ebfc50427009', NULL),
(108, 4, 2, 'ANDRIAMIHAJA', 'Davidson', 'andriamihaja@gmail.com', '0344729333', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '52102bd54d1fb941cb3de6407fb229dd', NULL),
(109, 4, 2, 'RAJOHANESA', 'Andriamiandrisoa Maminirina', 'ranjohanesa@gmail.com', '0340982191', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'f9009e167f9cf8428f345e09d8163535', NULL),
(110, 4, 2, 'RABARIJAONA', 'Nomenjanahary Riphun rison Jeremi', 'rabarijaona@gmail.com', '0347538368', NULL, '2000-06-02 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', 'b55aa9a95f9cc10c81483354d0d21829', 'M'),
(111, 4, 2, 'RAZAFINDRABE', 'Andoniaina Hasina', 'razafindrabe@gmail.com', '0382558712', NULL, '2000-04-09 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', 'c65e19268ea0ff1bb4fdce5303a49ae2', 'F'),
(112, 4, 2, 'RAMORASATA', 'Hajaharimanana', 'ramorasata@gmail.com', '0341704829', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '7a1cae48e59f1fba63897acc4897d831', NULL),
(113, 4, 2, 'RASAMIMANANA', 'Claude', 'rasamimanana@gmail.com', '033661474', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '630fdfa14251f2ce1540b82f4d8624e3', NULL),
(114, 4, 2, 'RAJAONARISON', 'Mamiarilala Mahefa', 'rajaonarison@gmail.com', '0347882076', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '99e0daa772172089baf7fba3aa834633', NULL),
(115, 6, 2, 'RANDRIANANJA', 'Bertrant', 'randriananja@gmail.com', '0348370973', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '09cbb5aee59de58c57fa4bc282c1448d', NULL),
(116, 6, 2, 'RAKOTOHAVANA', 'Arthur', 'rakotohavana@gmail.com', '0330220789', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '793bb0382044a2769082a675867cd1d5', NULL),
(117, 6, 2, 'JEAN', 'Benjamin David', 'benjamin@gmail.com', '0341141035', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'cfc1d1e8177c0814406f21d886a7d34a', NULL),
(118, 6, 2, 'RAKOTO', 'Feno', 'rakoto@gmail.com', '0384085342', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'a11db4798b14a4bc520a3c4a3b31b093', NULL),
(119, 6, 2, 'RANDRIAMANJAKA', 'J U Rolland', 'randriamanjaka@gmail.com', '0388051615', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'cd6fb54f83ce4f0480859071d42979c0', NULL),
(120, 6, 2, 'RAMANANJATO', 'Heritiana', 'ramananjato@gmail.com', '0345518918', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'c16623fc41811799cc9ef4f63c31f2c0', NULL),
(121, 6, 2, 'RAMARONIRIANA', 'Jacque', 'ramaroniriana@gmail.com', '0340734584', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'f4e60e8a40c38528462204a3b50c07a4', NULL),
(122, 6, 2, 'RANDRIAMANJATO', 'Modeste', 'randriamanjato@gmail.com', '0330485796', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'b7dbe07662f324dd7f241dd0db26ae3e', NULL),
(123, 6, 2, 'ANDRIAMAHAZO', 'Roel', 'andriamahazo@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '8c3fbba19b68f6ac0213a40f06aad900', NULL),
(124, 6, 2, 'RAKOTONDRABARY', 'Jean Rémi', 'rakotondrabary@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '1bb20a8ffa8f637fe585e4347a81c3bb', NULL),
(125, 6, 2, 'RAKOTOARIMANANA', 'Heritiana', 'rakotoarimanana@gmail.com', '0337626040', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '8e79e66d4165317acca1154788ef199c', NULL),
(126, 6, 2, 'RAKOTOZANANY', 'Jean Clément Isaie', 'rakotozanany@gmail.com', '0389636340', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '73eaec5a6d6990819c51dc197ff9d641', NULL),
(127, 6, 2, 'RANOMENJANAHARY', 'Hajatiana', 'ranomenjanahary@gmail.com', '0381769953', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '51243f2f5b5c3d12df8086ab036826be', NULL),
(128, 6, 2, 'RAKOTOARISOA', 'Mamy', 'rakotoarisoa@gmail.com', '0332176719', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'c0d23c5a92c47384721cee582c124bb3', NULL),
(129, 6, 2, 'RANDRIANASOLO', 'Fenotoky', 'randrianasolo@gmail.com', '0383776735', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'e5477d60a85867b50b2318611c3d078c', NULL),
(130, 6, 2, 'RAJARIVONY', 'Patrick Prosper', 'rajarivony@gmail.com', '0342832389', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'fa7f6458b418419adfdc00dfefb4db7c', NULL),
(131, 6, 2, 'RANDRIAMITA', 'Tso Gervais', 'randriamita@gmail.com', '0383867775', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '16a6635a8b265fa82e1c44eb74306de2', NULL),
(133, 6, 2, 'RASOLONIAINA', 'Faniry', 'faniry@gmail.com', '0387625507', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'fe512fb725ac30bff55b39749c88f3ca', NULL),
(134, 6, 2, 'HERIMAMPIONINA', 'Tahiniavo Fiobiana', 'tahiniavo@gmail.com', '0343603299', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'e9866959a130748da2182bed69458910', NULL),
(135, 6, 2, 'RAKOTOARISOA', 'Rijasoa', 'rijasoa@gmail.com', '0347459925', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '1609150c3a476688e1c9cade5e3f68ae', NULL),
(136, 6, 2, 'RAZAFIMAHATRATRA', 'Andry', 'andry@gmail.com', '0341414771', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '532d09ce53fdd08b95e3c0e9d24465e3', NULL),
(137, 6, 2, 'RAKOTOMALALA', 'Robert', 'rakotomalala@gmail.com', '0333180148', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '9a648d3926ed171579101f067d30c559', NULL),
(138, 6, 2, 'RAKOTOARIMALALA', 'Bruno', 'bruno@gmail.com', '0330494882', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'e29e4bbda6a1e0547440bae9284bcf8e', NULL),
(139, 6, 2, 'RANDRIARINIAINA', 'Rijasoa', 'randriariniaina@gmail.com', '0389026370', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '0081aa1662657b122ef5651cf9eae0e8', NULL),
(141, 6, 2, 'RAFALIMANANTSOA', 'Jean Claude', 'rafalimanantsoa@gmail.com', '0387365708', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'fcbdde6b63c3172be49d453eea086458', NULL),
(142, 3, 2, 'AVOTRINIAINA', 'Nomenjanahary Lalaina Solo-1', 'avotriniaina@gmail.com', '0385211037', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'f484d7a09c47f2b7ee9e2fe4745a4a59', NULL),
(143, 3, 2, 'RAMAROLAHY', 'Andriamorasata Jean B', 'andriamaroasata@gmail.com', '0389964823', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'a851db5a946820ddc895b1ad6c86996a', NULL),
(144, 3, 2, 'RABETOKOTANY', 'Jean De Dieu', 'rabetokotany@gmail.com', '0342076052', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'd80508ce123368204561edd80e34b7e2', NULL),
(145, 3, 2, 'RAKOTONIRIANA', 'Laurent', 'rakotonirina@gamil.com', '039725029', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '68ac936ba2c431f5ed11808749824709', NULL),
(146, 3, 2, 'RAMAMONJISOA', 'Falimanana Tsilavina Rolland', 'falimanana@gmail.com', '0341538376', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'c3e8433f26ebb442c39b3e6fed51f411', NULL),
(147, 3, 2, 'RAMANIVO', 'Tahiana', 'ramanivo@gmail.com', '03387987132', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '7d1ab88e06c44a476117261c8bb0fe4c', NULL),
(148, 3, 2, 'RANDRIANTSILAVINA', 'Gaston', 'randriantsilavina@gmail.com', '0345626898', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'f4594285f241fba1e6c5644065c96607', NULL),
(149, 3, 2, 'RAZAKASON', 'Fanomezana Tsiory Nantenaina', 'razakason@gmail.com', '0386444260', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'f70c82f98ec4bf2dbcf25a513bc7c28d', NULL),
(151, 3, 2, 'RAKOTOARISOA', 'Sitrakiniaina Tahiry', 'sitrakiniaina@gmail.com', '0382213447', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '891216615f9c73c1199dd335c532e12f', NULL),
(152, 3, 2, 'RANDRIAMANANKIERANA', 'Joelson', 'randriamanankierana@gmail.com', '0385875829', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '0c6c95097d197af17ddc9b11054e76dd', NULL),
(153, 3, 2, 'FANOMEZANTSOA', 'Fitahiana Lorca', 'lorca@gmail.com', '0347249702', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'dd96e5ec5fb22950e41c6d31fd7c1bfb', NULL),
(154, 3, 2, 'RANDRIANANTENAINA', 'William', 'randrianantenaina@gmail.com', '0349945674', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'e45cb2a74b1650084177cd4b03e38efc', NULL),
(155, 3, 2, 'VEROHANITRA', 'Aristide', 'verohanitra@gmail.com', '0349084019', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '483a9f1729d87c0fa27d60d4c1aca5ac', NULL),
(156, 3, 2, 'RABEARISOA', 'Mahery Fandresena', 'rabearisoa@gmail.com', '0341700454', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'b3c1d97c86b5048419b573bcd137ef3c', NULL),
(157, 3, 2, 'RANDRIAMANANTSOA', 'Solo Jean Josia', 'randriamanantsoa@gmail.com', '0388710810', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '9b7e7007282763cc70ff2944064ee464', NULL),
(158, 3, 2, 'RAKOTOARISON', 'David', 'rakotoarison@gmail.com', '0384761046', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'fb68e50cc4efd2c91248d197066a1115', NULL),
(159, 3, 2, 'ANDRIAMANAMPISOA', 'Jean Rolland', 'andriamanampisoa@gmail.com', '0388318015', NULL, '2001-04-19 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', '1f30fef9ed81f32e4d860523ff252d85', 'M'),
(160, 3, 2, 'ANDIAMANANA', 'Gilbert', 'andriamanana@gmail.com', '0345144117', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '83bff2aa93249e3ad1b2a8767dfb742e', NULL),
(161, 3, 2, 'FANILOTOKINIAINA', 'Benifaliana Nomenjanahary', 'fanilotokiniaina@gmail.com', '0347240931', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'c56f13e6ea638c1604e55a81e72e4bfc', 'M'),
(162, 3, 2, 'RAFIDSON', 'Dieu Donné', 'rafidson@gmail.com', '0382004193', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '0c2806420e7d7dccff19bb96e9a9490c', NULL),
(163, 5, 2, 'RAKOTONDRAPARANY', 'Njarasoa', 'rakotondraparany@gmail.com', '0344300890', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '3cc377c35e6266d59d04fe7dafb02c4b', NULL),
(164, 6, 2, 'RANDRIAMAHAZO', 'Roel', 'roel@gmail.com', '0348265090', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'c2d676fc33a895fb9c5c57d211997f0c', NULL),
(165, 2, 2, 'RANDRIANATOAVINDRAINY', 'Kotovaonirina Jean Jaques', 'randrianatoavindrainykotovaoni@gmail.com', '0383149115', NULL, '2005-06-29 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', 'd7cc6edd5e80bdee0b4bf0a2bc1ac531', 'M'),
(166, 6, 2, 'Fy', 'Mendrika', 'fymendrika@gmail.com', '0341234567', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '1750a86f015dcd1701d6c83c2662873f', 'F'),
(167, 4, 2, 'RAFANOMEZANTSOA', 'Zo Maminiaina Narindra', 'rafanomezantsoa@gmail.com', '0372763254', NULL, '2006-01-05 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', '48d0a802fac36d7ff62e0277ea6883f5', 'F'),
(168, 4, 2, 'RAKOTONDRAFARA', 'Mialitiana', 'rakotondrafara@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '88b0175d53a02155f1ff85dc98e24fa2', NULL),
(169, NULL, 2, 'RAZAFIARIVONY', 'Fenitra Elinah', 'fenitra@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '4743b4dc80f82c9826b42dffa52dbfe4', NULL),
(170, NULL, 2, 'RAHARILANTO', 'Miora', 'raharilanto@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '7d2876aa22047acbec8995f6fa49a164', NULL),
(171, 4, 2, 'RAJAONARIVONY', 'Maminiaina', 'maminiaina@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '1eb9af7d02e285fcb2f93bdb1f54429c', NULL),
(172, NULL, 2, 'FARANIAINA', 'Henintsoa', 'faraniaina@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '2b94f02bd48b86d8a574dcc2d3f988d6', NULL),
(173, NULL, 2, 'LANTOAVOTRANIAINA', 'Regi', 'regi@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'bb7753c4a12690e8dd983d1734d88714', NULL),
(174, 4, 2, 'RASOARIMALALA', 'Vonifanja Narindra', 'vonifanja@gmail.com', '0348892538', NULL, '1993-03-10 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', NULL, 'F'),
(175, 6, 2, 'NARIVELOSON', 'Francine Samson', 'francinesamson14@gmail.com', '0348613662', NULL, '1999-10-22 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', '137786d51d7ec3f16412423eb039ea03', 'F'),
(176, NULL, 2, 'FIFLIANTSOA', 'Esperance L', 'esperance@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'b2fa247e46604495c6660f9fad1acb9a', NULL),
(177, NULL, 2, 'RASOANANTENAINA', 'Prisca', 'rasoanantenaina@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '0742737ad5a3f77163ead8ba27691fd9', NULL),
(178, NULL, 2, 'AVAONORO', 'Olonirina Anitah', 'avaonoro@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'c5db49cbe29b2ebcfbc7acec9e58a83e', NULL),
(179, NULL, 2, 'RASOARIMALALA', 'H.Ortencia', 'ortencia@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '8945020f08555a1dfd7ba87a738b36f0', NULL),
(180, 2, 2, 'RASOARIMALALA', 'Nirina', 'rasoarimalala@gmail.com', NULL, NULL, '2004-04-17 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', '63c2ab934cbd8dd6e47fbdd01cdb821c', 'F'),
(181, 5, 2, 'RASOARIMALALA', 'Olga', 'olga@gmail.com', '0372665049', NULL, '1996-10-28 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', '6dd2e430d573811d800bd2041737178a', 'F'),
(182, NULL, 2, 'ANTRATIANA', 'Femenontsoa', 'famenontsoa@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '45392db71eaed9a0467b02919fcf8284', NULL),
(183, NULL, 2, 'NAMBININTSOA', 'Fitahiana', 'nambinintsoa@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '87b3c0ab0140a6d8e72296c4cbe65aa1', NULL),
(184, NULL, 2, 'NOMENJANAHARY', 'Mirantsoa', 'mirantsoa@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '4d5e6b6c3800a1661ae8f70b63a3feb8', NULL),
(185, NULL, 2, 'RAZAFINDRAFARA', 'Anjara O.M', 'anjara@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '279b3aff3563cd9e2d38187d5f704840', NULL),
(186, 2, 2, 'MENJANIAINA', 'Sylvie', 'sylvie@gmail.com', '0389104942', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'd23ac3e980afa919fd7f2769b2501827', 'F'),
(187, NULL, 2, 'RAHARISOA', 'Ravakiniaina Mbolaitana', 'mbolatiana@gamail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'fce9b26bf8159930b88625d6b9df5f78', NULL),
(188, NULL, 2, 'HATRINYAIANA', 'Nataly', 'nataly@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'e159e73e8c5908886b8118764f4318d9', NULL),
(189, NULL, 2, 'NOMENJANAHARY', 'Mirantsoa', 'nomenjanahary@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'aca4c4ccd334b5bf3a83de1542b01c17', NULL),
(190, NULL, 2, 'RAMANANTENASOA', 'Haingotiana Rose', 'haingotiana@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '0f620abcdc7b938ccdd25881a76e71f3', NULL),
(191, NULL, 2, 'NOMENJANAHARY', 'Kantoniaina Sylvia', 'kantoniaina@gmail.com', '0386653485', NULL, '2006-11-06 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', '13dc6100495520615c9c6ecabb20cb92', 'F'),
(192, NULL, 2, 'RISON', 'Jeremie', 'rison@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '1e8c84c0b90b50beaf1a206d0cbd98ec', NULL),
(193, NULL, 2, 'DIMBINIAINA', 'Regine', 'regine@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', NULL, NULL),
(194, NULL, 2, 'NALOBAVAKA', 'Tokiniaina', 'tokiniaina@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '579a7be64ccfca0061b2cf8e880f5b4d', NULL),
(195, NULL, 2, 'RAHARIMALALA', 'Vonitiana H', 'vonitiana@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '7f218fd1b30ac10dc87296844ef13e65', NULL),
(196, 5, 2, 'RASOAMANANA', 'Elysa', 'elysa@gmail.com', '0381187922', NULL, '2002-01-17 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', '9f2c284ec166e422adda88d1c71dd8fb', 'F'),
(197, 5, 2, 'ROVAMANGA', 'Julienne', 'julienne@gmail.com', '0381187922', NULL, '2006-10-25 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', 'c918c7d00fa207e273629dfd6b0f4641', 'F'),
(198, 2, 2, 'LAHIMADY', 'Jean Chrisostome', 'crisostome@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'c1ff844b75d020aae788170056a06b8b', NULL),
(199, 3, 2, 'ANDRIANANTENAINA', 'Véve', 'veve@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '937ffc4df6f8505bea227f432e7c3787', NULL),
(203, 5, 2, 'ANDRIANARAHINJAKA', 'Manantenasoa', 'manantenasoa@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '1e8db6c2a8f613e67ecfcd844047f128', NULL),
(204, 1, 2, 'RAKOARISOA', 'Mbolatsiky Rinah', 'rinah@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '6d21fcbc943e2b7bceddcf383c7528a7', NULL),
(205, 1, 2, 'RAKOTOZAFY', 'Nirina Finoana', 'rakotozafy@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '14608736abf5a2c0e4071a94a979a69e', NULL),
(206, 1, 2, 'RATSIMBAZAFY', 'F.Fifaliana', 'ratsimbazafy@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '0277c5438ac8662c8c741ff6da222b0b', NULL),
(207, 5, 2, 'TOJONIRINA', 'Tojonirina', 'tojonirina@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'e4cb635a0f35b7e1d2f5f20f8a1d55fd', NULL),
(208, 5, 2, 'SOLOFOHERISON', 'Rova Michel', 'solofoherison@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'c0c12b81c4a47fa2b0d2f11b6b45c9ef', NULL),
(209, 4, 2, 'RANDRIAMANANIRINA', 'Telitsoa MJ', 'telitsoa@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'e6c6d62aa12f2f3da55f7c791ef5f638', NULL),
(210, 2, 2, 'RANDRIANANTENAINA', 'Thiery', 'thiery@gmail.com', NULL, NULL, '1995-12-05 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', 'e9b6c2a5ee2e60c7f5dc4f690014ca42', 'M'),
(211, 4, 2, 'RABEARIVELO', 'Nirinasoa Ralf', 'ralf@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'a93d407aa74ed3bee0955f2124eaf6d2', NULL),
(212, 1, 2, 'RAKOTONIAINA', 'Claude David', 'rakotoniaina@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'a028951eb13fe65c70c5d3e51933b86a', NULL),
(213, 1, 2, 'RAKOTONDRAINY', 'Fanomezantsoa', 'rakotondrainy@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'b26e3b9759194e5bd5e98ad80b462e71', NULL),
(214, NULL, 2, 'ANDRIANARITA', 'Jean Marie', 'andrianarita@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '90dd535a78bc6ba592688b96e736d6c4', NULL),
(216, 4, 2, 'RANDRIANARIVONY', 'Hermane', 'hermane@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'e9c9cc5055ffefca54ea37c44477a6e8', NULL),
(217, 5, 2, 'RANDRIAMANTENA', 'Nomena Valisoa', 'nomena@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'b124e937c35479836363a1a48dbca3bf', NULL),
(218, 2, 2, 'ANDRIANJAFY', 'Seheno Horimanona', 'horimanona@gmail.com', '0346473120', NULL, '1988-08-23 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', 'da7314117538235774d677e98de8dc04', 'F'),
(219, 2, 2, 'RANDRIANANDRASANARIJAONA', 'Alain Gabriel', 'gabriel@gmail.com', '0384740177', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '79008ae6cbac641ef94d0c337739c8d8', 'M'),
(220, 2, 2, 'ANDRIANINA', 'NyONY Durland Revoatsy', 'revoatsy@gmail.com', '0387391963', NULL, '2006-05-22 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', 'c6f3990e1087f17ac4230dd1d7b8efc6', 'F'),
(221, 6, 2, 'TSIFERANIAINA', 'Solofonirina Martial', 'solofonirina@gamil.com', '0386640133', NULL, '2002-04-26 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', 'f964030016721f8bdfa8811e795a4fe0', 'M'),
(222, NULL, 2, 'RASOAMAMPIONONA', 'Bodo Voahangy Nirina', 'bodovoahangy@gmail.com', '0388518099', NULL, '1993-09-04 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', 'a4637185050d8627b9fc5674bc3b044e', 'F'),
(223, 1, 2, 'ANDRIAMAMENOSOA', 'Mamy Francia', 'andriamamenosoa@gmail.com', NULL, NULL, '2008-05-26 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', 'f7ea0e2945df1ca4d9baf714cd544b76', 'F'),
(224, 5, 2, 'RAFIDISON', 'Narindra Richinah', 'richinah@gmail.com', '0387911894', NULL, '2007-09-24 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', '1f3626e615b5eb2c01e37a7550bd6940', 'F'),
(225, 1, 2, 'RAVAOHARISOA', 'Nirina Fanjamalala', 'fanjamalala@gmail.com', '0344563609', NULL, '2006-05-29 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', '2a81e2a137972c43d6562f9e2b89ecc6', 'F'),
(226, 4, 2, 'RAZAFINDRABE', 'Nambinintsoa Fitahiana', 'razafindrabe28@gmail.com', '0345870468', NULL, '2005-08-28 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', '0ff87f9d910d41d1d9d1ebf9865f9be7', 'F'),
(227, 3, 2, 'ANDRIAMIHAJA', 'Andry Tiana Juliana', 'andrytianajuliana@gmail.com', '0388510655', NULL, '2008-02-11 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', 'e2ee51c3ed82fae6542a3e2cd9c1c86f', 'F'),
(228, 6, 2, 'RAHAROSETRA', 'Sahaza Tsinjo', 'tsinjoramarosetra@gmail.com', '0387984913', NULL, '2005-05-12 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', '83b9956550865612e09c17cf2c8a63b2', 'F'),
(229, 3, 2, 'MANANTENANIRINA', 'Fandresena', 'fandresemanantenanirina@gmail.com', '0380135248', NULL, '2007-12-08 00:00:00', NULL, NULL, '[\"ROLE_USER\"]', '8513f27e0ef24d99a2021f73025a63ea', 'F'),
(231, NULL, 2, 'RAKOTONIRINA', 'HenitsoaJ', 'henitsoa@gmail.com', '0383589757', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'c47cd53104c811a0795da0f2b9c7a373', NULL),
(232, NULL, 2, 'ARIVONY', 'Olivia Ju', 'ju@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'a432f096f750460afdbf93ad70cdd1ff', NULL),
(233, NULL, 2, 'MIARINIAINA', 'Tsiferanirina', 'tsiferanirina@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '6650340da6cae53f86b6ebdee3609838', NULL),
(234, NULL, 2, 'RAFANANTEANANA', 'SarobidyL', 'sarobidy@gmail.com', '0380860592', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'eb4290e1cd3ece808b41863c21e5ccff', NULL),
(235, NULL, 2, 'Fandresena', 'FanantenanaV', 'fandresena@gmail.com', '0360568829', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'e473c623d9716e630cbfd7b40325c2fa', NULL),
(236, NULL, 2, 'RAZAFINDRAIBE', 'NomenjanaharyJ', 'judichaella@gmail.com', '0386035011', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'd9b51f0c7140c9dd13b40a82ff9223f3', NULL),
(237, NULL, 2, 'HANITRINIAINA', 'TolojanaharyE', 'tolojanahary@gmail.com', '0386897866', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'a27dec91c3a22911665e5e36127db4bd', NULL),
(238, NULL, 2, 'Rakotondravony', 'Ny Avontsoa Ninah', 'nyavo@gmail.com', '0389581806', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '6bf848301463e87ce2ea3fe5b6f7fc43', NULL),
(239, NULL, 2, 'Rajaonarivony', 'Nehemia Mandresiniaina', 'mandresiniaina@gmail.com', '0348032043', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '6ad1c078a34880fd9bbd8ff7def942e3', NULL),
(240, NULL, 2, 'Razafindranoro', 'Nekena Fitahiana', 'nekenafitahiana@gmail.com', '0380877622', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '582820108095f8aa43a720bd00f47d53', NULL),
(241, NULL, 2, 'Rakotonirina', 'Miora Fahendrena Andrianah', 'miorafandresena@gmail.com', '0348284928', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '3000a74e72f714cc80c691efee4143d0', NULL),
(242, NULL, 2, 'Andrianantenaina', 'Helitiana Sarobidy', 'helitianasarobidy@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '946d931cc79538374c19ff05275721b3', NULL),
(243, NULL, 2, 'Ranjarivelo', 'Nirinasoa Ralphe', 'nirinasoa@gmail.com', '0389208225', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '1d5e5ac813e3aac6048993463478c90a', NULL),
(244, NULL, 2, 'Nirinaharisoalala', 'Fabrice', 'fabrice@gmail.com', '0382606924', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '0109ee28cb991ef71349726f0cfec2e4', NULL),
(245, NULL, 2, 'Randriamanalina', 'Nambinina', 'nambinina@gmail.com', '0334872016', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '609586ac246f16806aaa7953eef998ca', NULL),
(246, NULL, 2, 'Tolojanahary', 'Nomeniaina Finoana Prisca', 'nomenhanahary@gmail.com', '0381833962', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '46f4c4200ad8670869a4ad01aa7c3618', NULL),
(247, NULL, 2, 'Sendraniaina', 'Francine Olga', 'francineolga@gmail.com', '0349278551', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '5f2f22ab0e6afb5e11e401792c907be8', NULL),
(248, NULL, 2, 'Randriamampionona', 'Clément', 'randriamampionona@gmail.com', '0349278551', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'feed7ed6606d9bb0bbbe40e3c9a8d2f6', NULL),
(249, NULL, 2, 'Rasoarimalala', 'Fitiavaniaina', 'fitiavaniaina@gmail.com', '0349278551', NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', '3757d063de89fdca14703e9cd73a065c', NULL),
(250, NULL, 2, 'Rasoanambinina', 'Herimampionina', 'herimampionina@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'ebed140f8243f9bdbad295676abf4d4b', NULL),
(251, NULL, 2, 'Anjaratsiresy', 'Tanjonirina', 'tanjonirina@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'd3f7754ea60d53f2c0643e41bcb0b2af', NULL),
(252, NULL, 2, 'Anjaratsivery', 'Fenosoa', 'fenosoa@gmail.com', NULL, NULL, NULL, NULL, NULL, '[\"ROLE_USER\"]', 'a4c63e5aee5f79ea4a7dd7a54cda89c6', NULL);

-- --------------------------------------------------------

--
-- Structure de la table `membre_association`
--

CREATE TABLE `membre_association` (
  `membre_id` int(11) NOT NULL,
  `association_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `membre_association`
--

INSERT INTO `membre_association` (`membre_id`, `association_id`) VALUES
(1, 1),
(1, 3),
(2, 2),
(2, 3),
(3, 1),
(3, 3),
(4, 1),
(5, 1),
(5, 3),
(6, 1),
(8, 1),
(9, 1),
(10, 1),
(10, 3),
(11, 1),
(12, 1),
(13, 1),
(14, 1),
(15, 1),
(15, 3),
(16, 1),
(17, 1),
(17, 3),
(18, 1),
(18, 3),
(19, 1),
(20, 1),
(24, 1),
(25, 1),
(26, 1),
(27, 1),
(28, 1),
(28, 3),
(35, 1),
(36, 1),
(37, 1),
(37, 3),
(38, 1),
(39, 1),
(40, 1),
(41, 1),
(42, 1),
(43, 1),
(43, 3),
(44, 1),
(45, 1),
(46, 1),
(47, 1),
(71, 1),
(73, 1),
(74, 1),
(75, 1),
(75, 3),
(76, 1),
(77, 1),
(78, 1),
(78, 3),
(79, 1),
(80, 1),
(80, 3),
(85, 1),
(86, 1),
(87, 1),
(88, 1),
(89, 1),
(90, 1),
(91, 1),
(94, 1),
(95, 1),
(96, 1),
(97, 1),
(98, 1),
(99, 1),
(100, 1),
(100, 3),
(101, 1),
(102, 1),
(103, 1),
(104, 1),
(105, 1),
(107, 1),
(108, 1),
(109, 1),
(110, 1),
(110, 3),
(111, 1),
(111, 3),
(112, 1),
(113, 1),
(114, 1),
(115, 1),
(116, 1),
(117, 1),
(118, 1),
(119, 1),
(120, 1),
(121, 1),
(122, 1),
(123, 1),
(124, 1),
(125, 1),
(126, 1),
(126, 3),
(127, 1),
(128, 1),
(129, 1),
(130, 1),
(131, 1),
(133, 1),
(134, 1),
(135, 1),
(136, 1),
(137, 1),
(138, 1),
(139, 1),
(141, 1),
(142, 1),
(143, 1),
(144, 1),
(145, 1),
(146, 1),
(147, 1),
(148, 1),
(149, 1),
(151, 1),
(152, 1),
(153, 1),
(154, 1),
(155, 1),
(156, 1),
(157, 1),
(158, 1),
(159, 1),
(159, 3),
(160, 1),
(161, 1),
(161, 3),
(162, 1),
(163, 1),
(164, 1),
(165, 1),
(165, 3),
(166, 2),
(166, 3),
(167, 3),
(168, 3),
(169, 3),
(170, 3),
(171, 3),
(172, 3),
(173, 3),
(174, 3),
(175, 1),
(175, 3),
(176, 3),
(177, 3),
(178, 3),
(179, 3),
(180, 3),
(181, 3),
(182, 3),
(183, 3),
(184, 3),
(185, 3),
(186, 2),
(186, 3),
(187, 3),
(188, 3),
(189, 3),
(190, 3),
(191, 3),
(192, 3),
(193, 3),
(194, 3),
(195, 3),
(196, 3),
(197, 3),
(198, 3),
(199, 3),
(203, 3),
(204, 3),
(205, 3),
(206, 3),
(207, 3),
(208, 3),
(209, 3),
(210, 3),
(211, 3),
(212, 3),
(213, 3),
(214, 3),
(216, 3),
(217, 3),
(218, 3),
(219, 1),
(219, 3),
(220, 3),
(221, 1),
(221, 3),
(222, 3),
(223, 3),
(224, 2),
(224, 3),
(225, 2),
(225, 3),
(226, 3),
(227, 2),
(227, 3),
(228, 2),
(228, 3),
(229, 2),
(229, 3),
(231, 3),
(232, 3),
(233, 3),
(234, 3),
(235, 3),
(236, 3),
(237, 3),
(238, 3),
(239, 3),
(240, 3),
(241, 3),
(242, 3),
(243, 3),
(244, 3),
(245, 3),
(246, 3),
(247, 3),
(248, 3),
(249, 3),
(250, 3),
(251, 3),
(252, 3);

-- --------------------------------------------------------

--
-- Structure de la table `messenger_messages`
--

CREATE TABLE `messenger_messages` (
  `id` bigint(20) NOT NULL,
  `body` longtext NOT NULL,
  `headers` longtext NOT NULL,
  `queue_name` varchar(190) NOT NULL,
  `created_at` datetime NOT NULL COMMENT '(DC2Type:datetime_immutable)',
  `available_at` datetime NOT NULL COMMENT '(DC2Type:datetime_immutable)',
  `delivered_at` datetime DEFAULT NULL COMMENT '(DC2Type:datetime_immutable)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `note`
--

CREATE TABLE `note` (
  `id` int(11) NOT NULL,
  `contenu` longtext NOT NULL,
  `created_at` datetime NOT NULL COMMENT '(DC2Type:datetime_immutable)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `note`
--

INSERT INTO `note` (`id`, `contenu`, `created_at`) VALUES
(1, 'Très bien', '2026-09-17 06:54:32'),
(2, 'Animé', '2026-09-18 10:44:08');

-- --------------------------------------------------------

--
-- Structure de la table `permission`
--

CREATE TABLE `permission` (
  `id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  `feature_id` int(11) NOT NULL,
  `action` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `permission`
--

INSERT INTO `permission` (`id`, `role_id`, `feature_id`, `action`) VALUES
(1, 3, 2, 'READ'),
(2, 3, 2, 'WRITE'),
(3, 3, 2, 'ADMIN'),
(4, 3, 2, 'EXECUTE'),
(5, 3, 3, 'READ'),
(6, 3, 3, 'WRITE'),
(7, 3, 3, 'ADMIN'),
(8, 3, 3, 'EXECUTE'),
(9, 3, 4, 'READ'),
(10, 3, 4, 'WRITE'),
(11, 3, 4, 'ADMIN'),
(12, 3, 4, 'EXECUTE'),
(13, 3, 5, 'READ'),
(14, 3, 5, 'WRITE'),
(15, 3, 5, 'ADMIN'),
(16, 3, 5, 'EXECUTE'),
(17, 3, 7, 'READ'),
(18, 3, 7, 'WRITE'),
(19, 3, 7, 'ADMIN'),
(20, 3, 7, 'EXECUTE'),
(21, 3, 8, 'READ'),
(22, 3, 8, 'WRITE'),
(23, 3, 8, 'ADMIN'),
(24, 3, 8, 'EXECUTE'),
(25, 3, 9, 'READ'),
(26, 3, 9, 'WRITE'),
(27, 3, 9, 'ADMIN'),
(28, 3, 9, 'EXECUTE'),
(29, 3, 10, 'READ'),
(30, 3, 10, 'WRITE'),
(31, 3, 10, 'ADMIN'),
(32, 3, 10, 'EXECUTE'),
(33, 3, 11, 'READ'),
(34, 3, 11, 'WRITE'),
(35, 3, 11, 'ADMIN'),
(36, 3, 11, 'EXECUTE'),
(37, 3, 13, 'READ'),
(38, 3, 13, 'WRITE'),
(39, 3, 13, 'ADMIN'),
(40, 3, 13, 'EXECUTE'),
(41, 3, 14, 'READ'),
(42, 3, 14, 'WRITE'),
(43, 3, 14, 'ADMIN'),
(44, 3, 14, 'EXECUTE'),
(45, 3, 15, 'READ'),
(46, 3, 15, 'WRITE'),
(47, 3, 15, 'ADMIN'),
(48, 3, 15, 'EXECUTE'),
(49, 3, 16, 'READ'),
(50, 3, 16, 'WRITE'),
(51, 3, 16, 'ADMIN'),
(52, 3, 16, 'EXECUTE'),
(53, 3, 17, 'READ'),
(54, 3, 17, 'WRITE'),
(55, 3, 17, 'EXECUTE'),
(56, 3, 18, 'READ'),
(57, 3, 18, 'WRITE'),
(58, 3, 18, 'EXECUTE'),
(59, 3, 19, 'READ'),
(60, 3, 19, 'WRITE'),
(61, 3, 19, 'EXECUTE'),
(62, 3, 20, 'READ'),
(63, 3, 20, 'WRITE'),
(64, 3, 20, 'ADMIN'),
(65, 3, 20, 'EXECUTE'),
(66, 3, 21, 'READ'),
(67, 3, 21, 'WRITE'),
(68, 3, 21, 'ADMIN'),
(69, 3, 21, 'EXECUTE'),
(70, 3, 22, 'READ'),
(71, 3, 22, 'WRITE'),
(72, 3, 22, 'ADMIN'),
(73, 3, 22, 'EXECUTE');

-- --------------------------------------------------------

--
-- Structure de la table `presence`
--

CREATE TABLE `presence` (
  `id` int(11) NOT NULL,
  `membre_id` int(11) NOT NULL,
  `scanned_by_id` int(11) DEFAULT NULL,
  `activity_name` varchar(255) NOT NULL,
  `scanned_at` datetime NOT NULL COMMENT '(DC2Type:datetime_immutable)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `presence`
--

INSERT INTO `presence` (`id`, `membre_id`, `scanned_by_id`, `activity_name`, `scanned_at`) VALUES
(1, 1, NULL, 'Formation projet digital', '2026-08-30 11:32:44'),
(2, 3, NULL, 'Formation projet digital', '2026-08-30 11:33:39'),
(3, 3, 3, 'Formation des Jeunes 2026', '2026-09-07 17:03:06'),
(4, 85, NULL, 'Formation projet digital', '2026-09-14 15:12:55'),
(5, 1, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 09:51:25'),
(6, 19, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 10:28:10'),
(7, 110, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 10:29:05'),
(8, 47, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 10:29:46'),
(9, 43, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 10:30:41'),
(10, 131, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 10:31:02'),
(11, 15, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 10:31:15'),
(12, 124, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 10:31:49'),
(13, 91, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 12:50:11'),
(14, 120, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 12:50:32'),
(15, 134, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 12:51:11'),
(16, 126, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 12:51:31'),
(17, 164, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 12:55:34'),
(18, 165, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 12:58:14'),
(19, 159, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 17:24:08'),
(20, 3, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 17:24:16'),
(21, 78, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 17:24:50'),
(22, 161, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-15 21:37:08'),
(23, 158, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-16 00:20:02'),
(24, 162, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-16 00:20:42'),
(25, 145, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-16 00:25:06'),
(26, 135, NULL, 'Fiambenana Fiara sy Moto à 13h-15h', '2026-09-16 13:46:22'),
(27, 136, NULL, 'Fiambenana Fiara sy Moto à 13h-15h', '2026-09-16 13:46:59'),
(28, 97, NULL, 'Fiambenana Fiara sy Moto à 13h-15h', '2026-09-16 13:47:44'),
(29, 46, NULL, 'Fiambenana Fiara sy Moto à 13h-15h', '2026-09-16 13:48:29'),
(30, 158, NULL, 'Fiambenana Fiara sy Moto à 13h-15h', '2026-09-16 13:49:02'),
(31, 40, NULL, 'Fiambenana Fiara sy Moto à 13h-15h', '2026-09-16 13:53:35'),
(32, 103, NULL, 'Fiambenana Fiara sy Moto à 13h-15h', '2026-09-16 13:54:01'),
(33, 100, NULL, 'Fiambenana Fiara sy Moto à 13h-15h', '2026-09-16 13:54:24'),
(34, 28, NULL, 'Fiambenana Fiara sy Moto à 13h-15h', '2026-09-16 13:55:19'),
(35, 15, NULL, 'Fiambenana Fiara sy Moto à 13h-15h', '2026-09-16 13:55:43'),
(36, 161, NULL, 'Fiambenana Fiara sy Moto à 13h-15h', '2026-09-16 13:56:15'),
(37, 71, NULL, 'Fanangonana entana 16 Septembre', '2026-09-16 18:00:57'),
(38, 109, NULL, 'Fanangonana entana 16 Septembre', '2026-09-16 18:01:30'),
(39, 100, NULL, 'Fanangonana entana 16 Septembre', '2026-09-16 18:01:50'),
(40, 78, NULL, 'Fanangonana entana 16 Septembre', '2026-09-16 18:02:05'),
(41, 7, NULL, 'Fanangonana entana 16 Septembre', '2026-09-16 18:03:00'),
(42, 91, NULL, 'Fanangonana entana 16 Septembre', '2026-09-16 18:04:17'),
(43, 145, NULL, 'Fanangonana entana 16 Septembre', '2026-09-16 18:04:37'),
(44, 9, NULL, 'Fanangonana entana 16 Septembre', '2026-09-16 18:05:18'),
(45, 5, NULL, 'Fanangonana entana 16 Septembre', '2026-09-16 18:05:38'),
(46, 17, NULL, 'Fanangonana entana 16 Septembre', '2026-09-16 18:07:17'),
(47, 85, NULL, 'Fanangonana entana 16 Septembre', '2026-09-16 18:08:15'),
(48, 138, NULL, 'Fanangonana entana 16 Septembre', '2026-09-16 18:08:43'),
(49, 165, NULL, 'Fanangonana entana 16 Septembre', '2026-09-16 18:09:02'),
(50, 46, NULL, 'Fanangonana entana 16 Septembre', '2026-09-16 18:20:18'),
(51, 159, NULL, 'Fanangonana entana 16 Septembre', '2026-09-16 18:21:47'),
(52, 15, NULL, 'Fanangonana entana 16 Septembre', '2026-09-16 18:22:56'),
(53, 10, NULL, 'Fanangonana entana 16 Septembre', '2026-09-16 18:29:31'),
(54, 227, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-21 23:16:01'),
(55, 167, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-21 23:16:23'),
(56, 3, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-21 23:16:44'),
(57, 125, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-22 08:24:25'),
(58, 123, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-22 08:25:11'),
(59, 27, NULL, 'Fitaomana entana le 15 Septembre 2026', '2026-09-22 08:38:34'),
(60, 191, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 08:50:05'),
(61, 37, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 08:50:30'),
(62, 180, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 08:51:13'),
(63, 219, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 08:51:39'),
(64, 161, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 08:51:57'),
(65, 222, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 08:52:20'),
(66, 218, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 08:52:36'),
(67, 141, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 08:55:40'),
(68, 95, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 08:56:07'),
(69, 186, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 08:56:32'),
(70, 229, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 08:57:09'),
(71, 210, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 08:57:38'),
(72, 28, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 08:57:52'),
(73, 174, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 08:58:16'),
(74, 41, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 08:58:40'),
(75, 43, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 08:59:03'),
(76, 78, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:03:06'),
(77, 75, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:03:41'),
(78, 225, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:04:08'),
(79, 224, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:05:55'),
(80, 110, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:06:15'),
(81, 111, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:06:42'),
(82, 175, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:07:06'),
(83, 228, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:07:55'),
(84, 221, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:11:15'),
(85, 223, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:12:13'),
(86, 18, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:13:50'),
(87, 159, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:14:18'),
(88, 226, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:16:52'),
(89, 165, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:18:16'),
(90, 220, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:18:41'),
(91, 197, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:44:33'),
(92, 196, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:44:53'),
(93, 181, NULL, 'Fiofanan’ny tanora zokiny', '2026-09-22 09:45:27'),
(94, 3, NULL, 'TANORA SY NY FITIAVANA 18-10-2026', '2026-11-08 08:59:39'),
(95, 159, NULL, 'TANORA SY NY FITIAVANA 18-10-2026', '2026-11-08 08:59:50'),
(96, 231, NULL, 'Fiofanana Tanora zandriny (08-11-2026)', '2026-11-08 09:10:16'),
(97, 233, NULL, 'Fiofanana Tanora zandriny (08-11-2026)', '2026-11-08 09:10:30'),
(98, 232, NULL, 'Fiofanana Tanora zandriny (08-11-2026)', '2026-11-08 09:10:54'),
(99, 234, NULL, 'Fiofanana Tanora zandriny (08-11-2026)', '2026-11-08 09:11:30'),
(100, 235, NULL, 'Fiofanana Tanora zandriny (08-11-2026)', '2026-11-08 09:15:13'),
(101, 237, NULL, 'Fiofanana Tanora zandriny (08-11-2026)', '2026-11-08 09:21:32'),
(102, 236, NULL, 'Fiofanana Tanora zandriny (08-11-2026)', '2026-11-08 09:24:35'),
(103, 238, NULL, 'Fiofanana Tanora zandriny (08-11-2026)', '2026-11-08 09:29:53'),
(104, 239, NULL, 'Fiofanana Tanora zandriny (08-11-2026)', '2026-11-08 09:31:21'),
(105, 240, NULL, 'Fiofanana Tanora zandriny (08-11-2026)', '2026-11-08 09:33:55'),
(106, 241, NULL, 'Fiofanana Tanora zandriny (08-11-2026)', '2026-11-08 09:35:19'),
(107, 242, NULL, 'Fiofanana Tanora zandriny (08-11-2026)', '2026-11-08 09:36:11'),
(108, 37, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:49:58'),
(109, 17, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:50:23'),
(110, 3, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:50:35'),
(111, 221, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:51:07'),
(112, 43, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:51:18'),
(113, 229, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:51:40'),
(114, 224, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:52:01'),
(115, 167, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:52:21'),
(116, 131, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:52:38'),
(117, 181, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:52:49'),
(118, 161, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:53:00'),
(119, 213, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:53:56'),
(120, 100, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:54:09'),
(121, 197, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:54:27'),
(122, 196, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:54:43'),
(123, 227, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:54:54'),
(124, 228, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:55:03'),
(125, 243, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 08:58:25'),
(126, 78, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:00:36'),
(127, 244, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:00:47'),
(128, 110, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:01:05'),
(129, 219, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:01:35'),
(130, 245, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:04:02'),
(131, 18, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:04:20'),
(132, 1, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:04:40'),
(133, 166, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:04:49'),
(134, 220, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:10:42'),
(135, 159, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:10:54'),
(136, 225, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:11:21'),
(137, 191, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:11:55'),
(138, 171, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:13:15'),
(139, 223, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:15:28'),
(140, 246, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:17:22'),
(141, 175, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:17:37'),
(142, 174, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:18:01'),
(143, 177, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:18:25'),
(144, 210, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:18:36'),
(145, 75, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:19:17'),
(146, 41, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:19:33'),
(147, 218, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:20:55'),
(148, 126, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:26:03'),
(149, 180, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:26:56'),
(150, 193, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:29:16'),
(151, 247, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:38:25'),
(152, 248, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:39:33'),
(153, 165, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:48:56'),
(154, 10, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:56:03'),
(155, 127, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 09:59:05'),
(156, 5, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 10:03:32'),
(157, 45, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 10:09:09'),
(158, 249, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 10:10:33'),
(159, 250, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 10:24:35'),
(160, 185, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 10:25:12'),
(161, 251, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 10:26:11'),
(162, 252, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 10:33:25'),
(163, 172, NULL, 'Fiofanana Tanora zokiny', '2026-11-15 10:34:31');

-- --------------------------------------------------------

--
-- Structure de la table `role`
--

CREATE TABLE `role` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `role`
--

INSERT INTO `role` (`id`, `name`, `description`) VALUES
(1, 'FILOHAN\'NY SAMPANA LEHILAHY', 'Filohan\'ny Sampana Lehilahy'),
(2, 'TRESORIER SAMPANA LEHILAHY', 'Mpitantana ny volan\'ny sampana Lehilahy'),
(3, 'SECRETAIRE SAMPANA LEHILAHY', 'Mpitan-tsoratra Sampana Lehilahy'),
(4, 'CHEF DE GROUPE ADJOINT', 'FILOHA MPANDIMBY GROUPE'),
(5, 'SECRETAIRE GROUPE', 'Mpitan-tsoratra Groupe'),
(6, 'CHEF DE GROUPE', 'Filohan\'ny Groupe'),
(7, 'FILOHAN\'NY SAMPANA VEHIVAVY', 'Filohan\'ny sampana Vehivavy'),
(8, 'TRESORIER SAMPANA VEHIVAVY', 'Mpitam-bola sampana vehivavy'),
(9, 'SECRETAIRE SAMPANA VEHIVAVY', 'Mpitan-tsoratra Sampana Vehivavy'),
(10, 'MPIANDRAIKITRA TANORA', 'Mpiandraikitra Tanora');

-- --------------------------------------------------------

--
-- Structure de la table `role_assignment`
--

CREATE TABLE `role_assignment` (
  `id` int(11) NOT NULL,
  `membre_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  `fiangonana_context_id` int(11) DEFAULT NULL,
  `groupe_context_id` int(11) DEFAULT NULL,
  `association_context_id` int(11) DEFAULT NULL,
  `sous_groupe_context_id` int(11) DEFAULT NULL,
  `start_date` datetime NOT NULL COMMENT '(DC2Type:datetime_immutable)',
  `end_date` datetime DEFAULT NULL COMMENT '(DC2Type:datetime_immutable)',
  `exercice_year` varchar(10) NOT NULL,
  `is_active` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `role_assignment`
--

INSERT INTO `role_assignment` (`id`, `membre_id`, `role_id`, `fiangonana_context_id`, `groupe_context_id`, `association_context_id`, `sous_groupe_context_id`, `start_date`, `end_date`, `exercice_year`, `is_active`) VALUES
(1, 1, 1, NULL, NULL, 1, NULL, '2026-08-28 09:45:36', NULL, '2026', 1),
(2, 1, 10, NULL, NULL, 3, NULL, '2026-08-28 09:49:42', NULL, '2026', 1),
(3, 7, 6, 2, NULL, NULL, NULL, '2026-09-07 14:51:17', NULL, '2026', 1),
(4, 7, 6, 2, NULL, NULL, NULL, '2026-09-07 14:51:18', NULL, '2026', 1),
(5, 3, 3, 2, NULL, NULL, NULL, '2026-09-08 11:18:11', NULL, '2026', 1),
(8, 77, 6, 2, NULL, NULL, NULL, '2026-09-10 07:30:55', NULL, '2026', 1),
(12, 103, 6, 2, NULL, NULL, NULL, '2026-09-10 09:07:48', NULL, '2026', 1),
(13, 161, 6, 2, NULL, NULL, NULL, '2026-09-10 13:01:33', NULL, '2026', 1),
(14, 100, 2, NULL, NULL, 2, NULL, '2026-02-11 00:00:00', '2027-02-10 00:00:00', '2026', 1),
(15, 78, 3, NULL, NULL, 1, NULL, '2026-02-11 00:00:00', '2027-02-10 00:00:00', '2026', 1),
(16, 166, 10, NULL, NULL, 3, NULL, '2026-01-01 00:00:00', '2026-12-31 00:00:00', '2026', 1),
(17, 161, 6, 2, NULL, NULL, NULL, '2025-09-18 00:00:00', NULL, '2026', 1);

-- --------------------------------------------------------

--
-- Structure de la table `sous_groupe`
--

CREATE TABLE `sous_groupe` (
  `id` int(11) NOT NULL,
  `association_id` int(11) NOT NULL,
  `nom` varchar(255) NOT NULL,
  `description` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `type_evenement`
--

CREATE TABLE `type_evenement` (
  `id` int(11) NOT NULL,
  `nom` varchar(255) NOT NULL,
  `code` varchar(50) DEFAULT NULL,
  `description` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `type_evenement`
--

INSERT INTO `type_evenement` (`id`, `nom`, `code`, `description`) VALUES
(1, 'Fiofanan\'ny Tanora Zokiny', 'FORM_TAN_A', 'Fiofanan\'ny Tanora sokajy zokiny isam-bolana'),
(2, 'FIOFANAN\'NY TANORA SOKAJY ZANDRINY', 'FORM_TAN_B', 'Fiofanan\'ny tanora sokajy zandriny isaky ny 2 volana'),
(5, 'Fiambenana fiara sy moto 16 Septembre (13h-15h)', 'FiAra-moto', 'Fiambenana ny Fiara sy moto'),
(6, 'Fanagonana ny fitaovana noetina avy aty Andranovelona le 16 mirava', 'Pirina-entana', 'Fampitaovana entana'),
(7, 'Famereanana entana avy eny Andranomena le 17 Septembre', 'Famerenana', 'Fampitaovana miverina'),
(8, 'FIFANAN\'NY TANORA ZOKINY ANTANANARIVO', 'TANOR_le 20-09-2026', 'tanora vonona hiatrika ny fiavian\'JESOSY'),
(9, 'FIOFANAN\'NY TANORA ZOKINY', 'fiofanana_16Aout2026', 'tanora manoloana ny baikon\'JESOSY'),
(10, 'FIOFANANY TANORA ZOKINY 18-10-2026', 'FIOF_18-10-2026', 'TANORA SY NY FITIAVANA');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `association`
--
ALTER TABLE `association`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_FD8521CC5F9D98F6` (`fiangonana_id`);

--
-- Index pour la table `cotisation`
--
ALTER TABLE `cotisation`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_AE64D2ED6A99F74A` (`membre_id`),
  ADD KEY `IDX_AE64D2ED5F9D98F6` (`fiangonana_id`),
  ADD KEY `IDX_AE64D2EDEFB9C8A5` (`association_id`),
  ADD KEY `IDX_AE64D2ED7A45358C` (`groupe_id`),
  ADD KEY `IDX_AE64D2EDCB5FDB3E` (`enregistre_par_id`);

--
-- Index pour la table `don`
--
ALTER TABLE `don`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_F8F081D96A99F74A` (`membre_id`),
  ADD KEY `IDX_F8F081D95F9D98F6` (`fiangonana_id`),
  ADD KEY `IDX_F8F081D9EFB9C8A5` (`association_id`),
  ADD KEY `IDX_F8F081D97A45358C` (`groupe_id`),
  ADD KEY `IDX_F8F081D9CB5FDB3E` (`enregistre_par_id`);

--
-- Index pour la table `evenement`
--
ALTER TABLE `evenement`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_B26681E88939516` (`type_evenement_id`),
  ADD KEY `IDX_B26681E5F9D98F6` (`fiangonana_id`),
  ADD KEY `IDX_B26681E7A45358C` (`groupe_id`),
  ADD KEY `IDX_B26681EEFB9C8A5` (`association_id`);

--
-- Index pour la table `evenement_note`
--
ALTER TABLE `evenement_note`
  ADD PRIMARY KEY (`evenement_id`,`note_id`),
  ADD KEY `IDX_6CEE9F99FD02F13` (`evenement_id`),
  ADD KEY `IDX_6CEE9F9926ED0855` (`note_id`);

--
-- Index pour la table `feature`
--
ALTER TABLE `feature`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UNIQ_1FD7756677153098` (`code`);

--
-- Index pour la table `fiangonana`
--
ALTER TABLE `fiangonana`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UNIQ_55CF559D77153098` (`code`);

--
-- Index pour la table `groupe`
--
ALTER TABLE `groupe`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_4B98C215F9D98F6` (`fiangonana_id`);

--
-- Index pour la table `media`
--
ALTER TABLE `media`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_6A2CA10CFD02F13` (`evenement_id`);

--
-- Index pour la table `membre`
--
ALTER TABLE `membre`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UNIQ_F6B4FB29E7927C74` (`email`),
  ADD UNIQUE KEY `UNIQ_F6B4FB291BC9050B` (`qr_code_token`),
  ADD KEY `IDX_F6B4FB29355BDC74` (`zone_geographique_id`),
  ADD KEY `IDX_F6B4FB295F9D98F6` (`fiangonana_id`);

--
-- Index pour la table `membre_association`
--
ALTER TABLE `membre_association`
  ADD PRIMARY KEY (`membre_id`,`association_id`),
  ADD KEY `IDX_EEB303206A99F74A` (`membre_id`),
  ADD KEY `IDX_EEB30320EFB9C8A5` (`association_id`);

--
-- Index pour la table `messenger_messages`
--
ALTER TABLE `messenger_messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_75EA56E0FB7336F0E3BD61CE16BA31DBBF396750` (`queue_name`,`available_at`,`delivered_at`,`id`);

--
-- Index pour la table `note`
--
ALTER TABLE `note`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `permission`
--
ALTER TABLE `permission`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_E04992AAD60322AC` (`role_id`),
  ADD KEY `IDX_E04992AA60E4B879` (`feature_id`);

--
-- Index pour la table `presence`
--
ALTER TABLE `presence`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_6977C7A56A99F74A` (`membre_id`),
  ADD KEY `IDX_6977C7A5EBBC642F` (`scanned_by_id`);

--
-- Index pour la table `role`
--
ALTER TABLE `role`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UNIQ_57698A6A5E237E06` (`name`);

--
-- Index pour la table `role_assignment`
--
ALTER TABLE `role_assignment`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_BFF12E966A99F74A` (`membre_id`),
  ADD KEY `IDX_BFF12E96D60322AC` (`role_id`),
  ADD KEY `IDX_BFF12E963F4DF1D3` (`fiangonana_context_id`),
  ADD KEY `IDX_BFF12E96D3EDF013` (`groupe_context_id`),
  ADD KEY `IDX_BFF12E964BCBA375` (`association_context_id`),
  ADD KEY `IDX_BFF12E9612C825E4` (`sous_groupe_context_id`);

--
-- Index pour la table `sous_groupe`
--
ALTER TABLE `sous_groupe`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_D4A67ED6EFB9C8A5` (`association_id`);

--
-- Index pour la table `type_evenement`
--
ALTER TABLE `type_evenement`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UNIQ_BFE0290E77153098` (`code`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `association`
--
ALTER TABLE `association`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=54;

--
-- AUTO_INCREMENT pour la table `cotisation`
--
ALTER TABLE `cotisation`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT pour la table `don`
--
ALTER TABLE `don`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `evenement`
--
ALTER TABLE `evenement`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT pour la table `feature`
--
ALTER TABLE `feature`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT pour la table `fiangonana`
--
ALTER TABLE `fiangonana`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT pour la table `groupe`
--
ALTER TABLE `groupe`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT pour la table `media`
--
ALTER TABLE `media`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `membre`
--
ALTER TABLE `membre`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=253;

--
-- AUTO_INCREMENT pour la table `messenger_messages`
--
ALTER TABLE `messenger_messages`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `note`
--
ALTER TABLE `note`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT pour la table `permission`
--
ALTER TABLE `permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=74;

--
-- AUTO_INCREMENT pour la table `presence`
--
ALTER TABLE `presence`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=164;

--
-- AUTO_INCREMENT pour la table `role`
--
ALTER TABLE `role`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT pour la table `role_assignment`
--
ALTER TABLE `role_assignment`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT pour la table `sous_groupe`
--
ALTER TABLE `sous_groupe`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `type_evenement`
--
ALTER TABLE `type_evenement`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `association`
--
ALTER TABLE `association`
  ADD CONSTRAINT `FK_FD8521CC5F9D98F6` FOREIGN KEY (`fiangonana_id`) REFERENCES `fiangonana` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `cotisation`
--
ALTER TABLE `cotisation`
  ADD CONSTRAINT `FK_AE64D2ED5F9D98F6` FOREIGN KEY (`fiangonana_id`) REFERENCES `fiangonana` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_AE64D2ED6A99F74A` FOREIGN KEY (`membre_id`) REFERENCES `membre` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_AE64D2ED7A45358C` FOREIGN KEY (`groupe_id`) REFERENCES `groupe` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_AE64D2EDCB5FDB3E` FOREIGN KEY (`enregistre_par_id`) REFERENCES `membre` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_AE64D2EDEFB9C8A5` FOREIGN KEY (`association_id`) REFERENCES `association` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `don`
--
ALTER TABLE `don`
  ADD CONSTRAINT `FK_F8F081D95F9D98F6` FOREIGN KEY (`fiangonana_id`) REFERENCES `fiangonana` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_F8F081D96A99F74A` FOREIGN KEY (`membre_id`) REFERENCES `membre` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_F8F081D97A45358C` FOREIGN KEY (`groupe_id`) REFERENCES `groupe` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_F8F081D9CB5FDB3E` FOREIGN KEY (`enregistre_par_id`) REFERENCES `membre` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_F8F081D9EFB9C8A5` FOREIGN KEY (`association_id`) REFERENCES `association` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `evenement`
--
ALTER TABLE `evenement`
  ADD CONSTRAINT `FK_B26681E5F9D98F6` FOREIGN KEY (`fiangonana_id`) REFERENCES `fiangonana` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_B26681E7A45358C` FOREIGN KEY (`groupe_id`) REFERENCES `groupe` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_B26681E88939516` FOREIGN KEY (`type_evenement_id`) REFERENCES `type_evenement` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_B26681EEFB9C8A5` FOREIGN KEY (`association_id`) REFERENCES `association` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `evenement_note`
--
ALTER TABLE `evenement_note`
  ADD CONSTRAINT `FK_6CEE9F9926ED0855` FOREIGN KEY (`note_id`) REFERENCES `note` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_6CEE9F99FD02F13` FOREIGN KEY (`evenement_id`) REFERENCES `evenement` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `groupe`
--
ALTER TABLE `groupe`
  ADD CONSTRAINT `FK_4B98C215F9D98F6` FOREIGN KEY (`fiangonana_id`) REFERENCES `fiangonana` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `media`
--
ALTER TABLE `media`
  ADD CONSTRAINT `FK_6A2CA10CFD02F13` FOREIGN KEY (`evenement_id`) REFERENCES `evenement` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `membre`
--
ALTER TABLE `membre`
  ADD CONSTRAINT `FK_F6B4FB29355BDC74` FOREIGN KEY (`zone_geographique_id`) REFERENCES `groupe` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_F6B4FB295F9D98F6` FOREIGN KEY (`fiangonana_id`) REFERENCES `fiangonana` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `membre_association`
--
ALTER TABLE `membre_association`
  ADD CONSTRAINT `FK_EEB303206A99F74A` FOREIGN KEY (`membre_id`) REFERENCES `membre` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_EEB30320EFB9C8A5` FOREIGN KEY (`association_id`) REFERENCES `association` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `permission`
--
ALTER TABLE `permission`
  ADD CONSTRAINT `FK_E04992AA60E4B879` FOREIGN KEY (`feature_id`) REFERENCES `feature` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_E04992AAD60322AC` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `presence`
--
ALTER TABLE `presence`
  ADD CONSTRAINT `FK_6977C7A56A99F74A` FOREIGN KEY (`membre_id`) REFERENCES `membre` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_6977C7A5EBBC642F` FOREIGN KEY (`scanned_by_id`) REFERENCES `membre` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `role_assignment`
--
ALTER TABLE `role_assignment`
  ADD CONSTRAINT `FK_BFF12E9612C825E4` FOREIGN KEY (`sous_groupe_context_id`) REFERENCES `sous_groupe` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_BFF12E963F4DF1D3` FOREIGN KEY (`fiangonana_context_id`) REFERENCES `fiangonana` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_BFF12E964BCBA375` FOREIGN KEY (`association_context_id`) REFERENCES `association` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_BFF12E966A99F74A` FOREIGN KEY (`membre_id`) REFERENCES `membre` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_BFF12E96D3EDF013` FOREIGN KEY (`groupe_context_id`) REFERENCES `groupe` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_BFF12E96D60322AC` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `sous_groupe`
--
ALTER TABLE `sous_groupe`
  ADD CONSTRAINT `FK_D4A67ED6EFB9C8A5` FOREIGN KEY (`association_id`) REFERENCES `association` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
