async function readProfile() {
  try {
    const response = await fetch("cv-files/" + lang + ".json");
    const text = await response.text();
    const data = JSON.parse(text);
    return data;
  } catch (error) {
    console.error("Error:", error);
  }
}

function createLink(key, text) {
  switch (key) {
    case "email":
      return "<a href='mailto:" + text + "'>" + text + "</a>";
    case "phone":
      // remove dashes, spaces, / and + from phone number
      var phone = text.replace(/[-\s\/+]/g, "");
      return "<a href='tel:" + phone + "'>" + text + "</a>";
    case "website":
      var url = text;
      // if the url doesn't start with http or https, add http
      if (!url.match(/^(http|https):\/\//)) {
        url = "https://" + url;
      }
      return "<a href='" + url + "'>" + text + "</a>";
    case "linkedin":
      // extract the username from the text provided
      var username = text.split("/").pop();
      // if the text isn't a full URL, add the LinkedIn domain
      if (!text.match(/^(http|https):\/\//)) {
        text = "https://www.linkedin.com/in/" + username;
      }
      return "<a href='" + text + "'>" + username + "</a>";
    default:
      return text;
  }
}

// Read icons from JSON file
let iconClasses;
async function loadIconClasses() {
  const response = await fetch("cv-files/icons.json");
  iconClasses = await response.json();
}
loadIconClasses();

function addIcons(key) {
  // Get the icon class for the key
  var iconClass = iconClasses[key];
  // If there's no icon class for the key, return an empty string
  if (!iconClass) return "";
  // Otherwise, return an i element with the icon class
  return "<i class='" + iconClass + "'></i> ";
}

async function displayProfile() {
  const rawProfile = await readProfile();
  var name = "";
  var profile = "";
  for (var key in rawProfile) {
    if (key == "name") {
      name = "<h1 id='" + key + "'>" + rawProfile[key] + "</h1>";
    } else if (key == "title") {
      name += "<h2 id='" + key + "'>" + rawProfile[key] + "</h2>";
    } else {
      // Add to profile: li containing i with icon and span with content
      profile +=
        "<li id='" +
        key +
        "'>" +
        addIcons(key) +
        "<span class='profile-entry'>" +
        createLink(key, rawProfile[key]) +
        "</span>" +
        "</li>";
    }
  }
  profile = name + "<ul class='profile list-unstyled'>" + profile + "</ul>";
  return profile;
}

export { displayProfile };
