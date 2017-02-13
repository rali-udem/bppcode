/*
 * This AngularJS controls BPPGen's web application.
 * Functions are named to make debugging easier.
 * Author: Philippe Grand'Maison.
 */


/* = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
 * UTILS AND CONSTS
 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = */

/*
 * @returns a clone
 */

function clone(obj) {
	return JSON.parse(JSON.stringify(obj))
}

DEFAULT_LANG = "en";

const I18N = {
		"en" : {
			"other_lang" : "fr",
			"words" : "words",
			"offer" : {
				"next" : "Next",
				"load_offer" : "Load offer",
				"search" : "Offer id or keyword:",
				"company_name" : "Company name",
				"place" : "Place",
				"descr" : "Description",
				"title" : "Title"
			},
			"profile" : {
				"empty_profile_list" : "No candidate was selected.",
				"new_candidate_button" : "New candidate",
				"confirm_candidate_button" : "Add to list",
				"load_profile" : "Load profile",
				"cancel" : "Cancel",
				"search" : "Profile id or keyword:",
				"branding_claim" : "Branding claim",
				"branding_pitch" : "Branding pitch",
				"skills" : "Skills",
				"message_label" : "Message",
				"message_button" : "Generate",
				"experiences" : "Experiences",
				"hide" : "Hide",
				"function" : "Function",
				"start_date" : "Start date",
				"end_date" : "End date",
				"mission" : "Mission"
			},
			"navbar" : {
				"start" : "Start",
				"about" : "About",
				"help" : "Help"
			}
		},
		"fr" : {
			"other_lang" : "en",
			"words" : "mots",
			"offer" : {
				"next" : "Continuer",
				"load_offer" : "Charger l'offre",
				"search" : "ID ou mots-clé de l'offre:",
				"company_name" : "Nom de compagnie",
				"place" : "Endroit",
				"descr" : "Description",
				"title" : "Titre"
			},
			"profile" : {
				"empty_profile_list" : "Aucun candidat n'est sélectionné.",
				"new_candidate_button" : "Nouveau candidat",
				"confirm_candidate_button" : "Ajout à la liste",
				"load_profile" : "Charger le profil",
				"cancel" : "Annuler",
				"search" : "ID ou mots-clé du profil",
				"branding_claim" : "Marque personnelle (court)",
				"branding_pitch" : "Marque personnelle (lang)",
				"skills" : "Compétences",
				"message_label" : "Message",
				"message_button" : "Générer",
				"experiences" : "Expériences",
				"hide" : "Cacher",
				"function" : "Fonction",
				"start_date" : "Date de début",
				"end_date" : "Date de fin",
				"mission" : "Mission"
			},
			"navbar" : {
				"start" : "Commencer",
				"about" : "À propos",
				"help" : "Aide"
			}
		}
};


const ALERT_DURATION = 3000;
const SNIPPET_LENGTH = 40;
const DUMMY_ID = "custom";
const DEFAULT_OFFER_ID = "55157f72c51c771c4bc36fd9";
const DEFAULT_PROFILE_ID = "52b31a870b045119318b4567";
const DEFAULT_EXPERIENCE = {"startDate":"",
		"function":"",
		"place":"",
		"companyName":""};
const DEFAULT_SKILL = {"name" : ""};
const LONG_PROFILE = {
		"countryCode":"CA",
		"city":"Montreal",
		"personalBranding_claim":"",
		"personalBranding_pitch":"",
		"experiences":[
			{"startDate":"2014-05","function":"CFO","place":"Montreal","companyName":"Skynet Inc."},
			{"startDate":"2013-04","function":"CFO","place":"Toronto","companyName":"Acme Corp."},
			{"startDate":"2011-03",
				"endDate":"2013-01",
				"function":"President \u0026 COO",
				"place":"Toronto, Canada Area",
				"missions":"Visual Effects intellectual property acquisitions, Co-Productions leadership",
				"companyName":"Acme Corp.",},
			{"startDate":"2007-07","endDate":"2011-03",
				"function":"VP Finance \u0026 Business Development",
				"missions":"",
				"companyName":"Acme Corp."}],
		"skills":[{"name":"Business Development"},{"name":"Strategy"},{"name":"Mergers"},{"name":"Budgets"},{"name":"Business Strategy"},{"name":"Management"},{"name":"Feature Films"},{"name":"Film"},{"name":"Animation"},{"name":"Project Management"},{"name":"Debt \u0026 Equity Financing"},{"name":"Leadership"},{"name":"Strategic Planning"},{"name":"Business Planning"},{"name":"Marketing"},{"name":"Visual Effects"},{"name":"Team Building"},{"name":"Negotiation"},{"name":"Film Production"},{"name":"Finance"},{"name":"Digital Media"},{"name":"Project Planning"},{"name":"Computer Animation"},{"name":"Contract Negotiation"},{"name":"Mergers \u0026 Acquisitions"},{"name":"Character Animation"},{"name":"Operations Management"}],
		"language":"en",
};
const DEFAULT_OFFER = {
		"description" : "",
		"title" : "",
		"place" : "",
		"company_name" : ""
	};
const DEFAULT_PROFILE = {
		"countryCode":"",
		"city":"",
		"personalBranding_claim":"",
		"personalBranding_pitch":"",
		"experiences":[],
		"skills":[],
		"language":"",
};

const OTHER_DATA = {
        "lang" : "en",
        "formality" : 1,
         "psy" : "D"
	};


var app = angular.module("bpp", ["ngRoute"]);
/* = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
 * ROUTES
 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = */
app.config(function($routeProvider) {
    $routeProvider
    .when("/bppgen/about", {
        templateUrl : "about.htm"
    })
    .when("/bppgen/help", {
        templateUrl : "help.htm"
    })
    .when("/bppgen/:lang/offer", {
        templateUrl : "offer.htm",
        controller : "OfferController"
    })
    .when("/bppgen/:lang/offer/:offerId", {
        templateUrl : "offer.htm",
        controller : "OfferController"
    })
    .when("/bppgen/:lang/offer/:offerId/candidates", {
        templateUrl : "choose_candidates.htm",
        controller : "CandidatesController"
    })
    .when("/bppgen/:lang/offer/:offerId/candidates/:candidateIdList", {
        templateUrl : "choose_candidates.htm",
        controller : "CandidatesController"
    })
});
/* = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
 * ASYNC CALLS SERVICE
 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = */
app.service('BPPService', ['$http', function ($http) {
	
	function loadProfile(profileRequest) { return $http.get('api/profile/' + profileRequest)};
	
	function loadOffer(offerRequest) { return $http.get('api/offer/' + offerRequest)};
	
	function generateLetter(offer, profile, lang) {
		var other_data = clone(OTHER_DATA);
		other_data["lang"] = lang;
		const generation_data = {
				'offer' : offer,
				'profile' : profile,
				'other' : other_data
		};
		return $http.post('letter', generation_data);
	}
	
	this.loadOffer = loadOffer;
	this.loadProfile = loadProfile;
	this.generateLetter = generateLetter;
}]);

app.controller('MasterController', ['$timeout', '$routeParams', '$location', '$scope',
	function ($timeout, $routeParams, $location, $scope) {
		$scope.offer = null;
		$scope.warning = null;
		if ($routeParams.lang) {
			$scope.lang = $routeParams.lang;
		}
		else {
			$scope.lang = DEFAULT_LANG;
		}
		$scope.i18n = I18N;
		
		function set_lang(other_lang) {
			$location.path("/bppgen/" + other_lang + "/offer");
			$scope.lang = other_lang;
		}
		
		function warn_user(message) {
			$scope.warning = message;
			$timeout(function() {
				$scope.warning = null;
			}, ALERT_DURATION);
		}
		$scope.warn_user = warn_user;
		$scope.set_lang = set_lang;
}]);

app.controller('OfferController', ['BPPService', '$route', '$routeParams', '$scope',
	function (BPPService, $route, $routeParams, $scope) {
	
	$scope.editable_offer = false;
	
	if (!$scope.offerId && $routeParams.offerId) {
		$scope.offerId = $routeParams.offerId;
	}
	
	function loadOffer() {
		BPPService.loadOffer($scope.offerId).then(function (response) {
			if (!response.data.hasOwnProperty('description')) {
				$scope.$parent.warn_user("Offer '" + $scope.offerId + "' not found.");
				$scope.$parent.offer = DEFAULT_OFFER;
				$scope.editable_offer = true;
				$scope.offerId = "";
				
			}
			else {
				$scope.$parent.offer = response.data;
				if ($scope.offer.hasOwnProperty('id')) {
					$scope.offerId = $scope.offer['id'];
				}
			}
		});
	}
	
	$scope.next = function() {
		if (!$scope.offerId) {
			return DUMMY_ID;
		}
		return $scope.offerId;
	};
	$scope.loadOffer = loadOffer;
}]);

app.controller('CandidatesController', ['BPPService','$route', '$routeParams', '$scope', '$q',
	function (BPPService, $route, $routeParams, $scope, $q) {
	$scope.data = {profileId : ""};//This is in an object because immutable types are bad at two-way binding!
	$scope.candidateList = [];
	$scope.message_paragraphs = {};
	$scope.profile = null;
	$scope.active_index = null;
	$scope.new_candidate = false;
	
	function activate(index) {
		$scope.profile = $scope.candidateList[index];
		$scope.active_index = index;
	}
	function deactivate() {
		$scope.profile = null;
		$scope.data.profileId = "";
	}
	
	/* = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
	 * ASYNC
	 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = */
	
	function generate() {
		BPPService.generateLetter(
				$scope.$parent.offer, $scope.profile, $scope.$parent.lang)
				.then(function(response){
					var letter = response.data;
					$scope.message_paragraphs[$scope.active_index] = letter.split('\n');
				},
				 function(response) {
					console.log('ERROR:' + response);
				});
	}
	
	function loadProfile(){
		BPPService.loadProfile($scope.data.profileId).then(function (response) {
			if (!response.data.hasOwnProperty('skills')) {
				$scope.$parent.warn_user("Profile '" + $scope.data.profileId + "' not found.");
				$scope.profile = DEFAULT_PROFILE;
				$scope.data.profileId = "";
			}
			else {
				$scope.profile = response.data;
				if ($scope.profile.hasOwnProperty('id')) {
					$scope.data.profileId = $scope.profile['id'];
				}
			}
		});
	}
	
	

	/* = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
	 * UI
	 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = */

	
	function add_candidate() {
		$scope.new_candidate = true;
		$scope.profile = clone(DEFAULT_PROFILE);
	}
	
	function save_candidate() {
		$scope.new_candidate = false;
		$scope.candidateList.push($scope.profile);
	}
	
	function cancel_candidate() {
		$scope.new_candidate = false;
		$scope.profile = null;
	}
	
	function profile_snippet(profile) {
		var snippet = "";
		if (profile.personalBranding_claim) {
			snippet = profile.personalBranding_claim;
		}
		else if (profile.experiences) {
			var last_experience = profile.experiences[0];
			if (last_experience.hasOwnProperty('function')) {
				snippet = last_experience[0];
			}
		}
		if (!snippet) {
			snippet = "NO DESCRIPTION";
		}
		if (snippet.length > SNIPPET_LENGTH) {
			snippet= snippet.substring(0, SNIPPET_LENGTH - 3) + '...';
		}
		return snippet.substring(0, SNIPPET_LENGTH);
	}
	
	function add_skill(){
		$scope.profile.skills.push(clone(DEFAULT_SKILL));
	}
	
	function add_experience(){
		$scope.profile.experiences.push(clone(DEFAULT_EXPERIENCE));
	}
	/* = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
	 * INIT
	 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = */
	/**
	 * This function fetches the ids in the candidate list passed as parameters after creation.
	 */
	function init_candidates() {
		var profile_promises = [];
		if ($routeParams.candidateIdList) {
			var ids = $routeParams.candidateIdList.split('+');
			var l = ids.length;
			for (var i = 0 ; i < l; i++) {
				var fetch_promise = BPPService.loadProfile(ids[i]);
				profile_promises.push(
						fetch_promise.then(function(response){
							if (response.data.hasOwnProperty('skills')) {
								$scope.candidateList.push(response.data);
							}
							})
				);
			}
		}
		return $q.all(profile_promises);
	}
	/**
	 * This function fetches the offer after creation.
	 */
	function init(){
		init_candidates().then(function() {
		if (!$scope.$parent.offer && $routeParams.offerId) {
			BPPService.loadOffer($routeParams.offerId).then(
					function (response) {
						if (!response.data.hasOwnProperty('description')) {
							$scope.$parent.offer = DEFAULT_OFFER;
						}
						else {
							$scope.$parent.offer = response.data;
						}});}});}
	$scope.profile_snippet = profile_snippet;
	$scope.loadProfile = loadProfile;
	$scope.add_experience = add_experience;
	$scope.add_skill = add_skill;
	$scope.cancel_candidate = cancel_candidate;
	$scope.save_candidate = save_candidate;
	$scope.add_candidate = add_candidate;
	$scope.generate = generate;
	$scope.activate = activate;
	$scope.deactivate = deactivate;
	init();
}]);