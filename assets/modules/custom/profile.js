import $ from "jquery";

async function readProfile() {
  try {
    const response = await fetch("cv-files/" + lang + ".json");
    const data = await response.json();
    // Use the parsed JSON data here
    console.log(data);
    return data;
  } catch (error) {
    console.error("Error:", error);
  }
}

function createLink(text) {
  // regex for email, phone and website
  var emailRegex = /^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)*$/i;
  var phoneRegex = /^(\+\d{1,3}\s?)?((\(\d{1,3}\))|\d{1,3})[-.\s]?\d{1,4}[-.\s]?\d{1,9}$/;
  var websiteRegex = /((https?:\/\/)?(www\.)?[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+)/;

  // match the regex
  var emailMatch = text.match(emailRegex);
  var phoneMatch = text.match(phoneRegex);
  var websiteMatch = text.match(websiteRegex);

  if (emailMatch) {
    return "<a href='mailto:" + emailMatch[0] + "'>" + emailMatch[0] + "</a>";
  } else if (phoneMatch) {
    // remove dashes, spaces, / and + from phone number
    var phone = phoneMatch[0].replace(/[-\s\/+]/g, "");
    return "<a href='tel:" + phone + "'>" + phoneMatch[0] + "</a>";
  } else if (websiteMatch) {
    return "<a href='" + websiteMatch[0] + "'>" + websiteMatch[0] + "</a>";
  }
  // else return the original text
  else {
    return text;
  }
}

async function displayProfile() {
    const rawProfile = await readProfile();
    var name = "";
    var profile = "";
    for (var key in rawProfile) {
        if (key == "name") {
            name = "<h1 id='" + key + "'>" + rawProfile[key] + "</h1>";
        } else {
            profile += "<li id='" + key + "'>" + createLink(rawProfile[key]) + "</li>";
        }
    }
    profile = name + "<ul class='profile'>" + profile + "</ul>";
    return profile;
}

export { displayProfile };
