(() => {
    var renew_ftoken = {};
    function ftoken_field_key(event) {
        document.querySelectorAll('.ftoken-field-key').forEach((e) => {
            e.classList.remove('ftoken-field-key');
            function set_ftoken_field() {
                e.form.querySelectorAll('[type=submit]').forEach((e) => { e.disabled = true });
                clearTimeout(renew_ftoken[e.dataset.ftokenid]);
                if (e.value.trim() !== "") {
                    let ftoken = document.getElementById(e.dataset.ftokenid)
                    let url = ftoken.dataset.url + '/' + CryptoJS.SHA256(e.value).toString() + '/' + e.dataset.ftokenid + '/' + e.form.id;
                    neutral_fetch(ftoken, url, ftoken.dataset.wrap);
                    renew_ftoken[e.dataset.ftokenid] = setTimeout(() => {
                        // Renew token before expiration
                        set_ftoken_field()
                    }, FTOKEN_EXPIRES_SECONDS * 1000 - 2000);
                }
            }
            e.addEventListener('change', set_ftoken_field);
            set_ftoken_field()
        });
    }

    function ftoken_field_ftoken(event) {
        document.querySelectorAll('.ftoken-field-ftoken').forEach((e) => {
            e.classList.remove('ftoken-field-ftoken');
            let form = document.getElementById(e.dataset.formid);
            if (form.querySelector('.ftoken-field-value').value.trim() !== "") {
                form.querySelectorAll('[type=submit]').forEach((e) => { e.disabled = false });
            }
        });
    }

    function ftoken_OnfocusReset() {
        document.querySelectorAll('[data-ftoken-onfocus-reset]').forEach(input => {
            input.addEventListener('focus', function() {
                const checkboxId = this.dataset.ftokenOnfocusReset;
                const checkbox = document.getElementById(checkboxId);
                if (checkbox) { checkbox.checked = false; }
            });
        });
        document.querySelectorAll('[data-ftoken-onclick-remove]').forEach(element => {
            element.addEventListener('click', function() {
                const elementIdToRemove = this.dataset.ftokenOnclickRemove;
                const elementToRemove = document.getElementById(elementIdToRemove);
                if (elementToRemove) { elementToRemove.remove(); }
            });
        });
    }

    function sbase64url_sha256_encode(str) {
        const sha256 = CryptoJS.SHA256(str);
        const base64 = sha256.toString(CryptoJS.enc.Base64);
        return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    }

    function sbase64url_encode(str) {
        const encoder = new TextEncoder();
        const uint8Array = encoder.encode(str);
        const binString = String.fromCodePoint(...uint8Array);
        const base64 = btoa(binString);
        return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    }

    // If the form with ftoken is on a page
    window.addEventListener('load', (event) => {
        // the order of execution is important
        ftoken_field_ftoken(event);
        ftoken_field_key(event);
        ftoken_OnfocusReset()
    });

    // If the form with ftoken is on a page loaded with ajax
    window.addEventListener('neutralFetchCompleted', (event) => {
        // the order of execution is important
        ftoken_field_ftoken(event);
        ftoken_field_key(event);
        ftoken_OnfocusReset()
    });

})();
