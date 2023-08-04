function isValidForm(event) {
    age = document.getElementById('age');

    age_num = age.value;

    if (age_num > 0 && age_num < 13) {
        event.preventDefault();
        alert("Sorry Your to young to make an account :(");
        window.location.replace("/");

    }
}