// start: Klientside-kryptering av kommentar før innsending - oppfyller F1 (privat kommentar) og NF7 (kryptering og nøkkelhåndtering i klient) (person 3)
const form = document.querySelector("#bidrag-form");

if (form) {
  const emailField = document.querySelector("#epost");
  const passwordField = document.querySelector("#passord");
  const commentField = document.querySelector("#kommentar");
  const metadataField = document.querySelector("#offentlig_nokkel");
  const statusField = document.querySelector("#kryptering-status");
  const submitButtons = Array.from(document.querySelectorAll(".buttons input[type='submit']"));

  const ACTIONS_WITH_ENCRYPTION = new Set(["Ny", "Endre"]);
  const PBKDF2_ITERATIONS = 150000;
  const MAX_COMMENT_BYTES = 700;
  let skipNextEncryption = false;

  const encoder = new TextEncoder();

  function findSubmitter(event) {
    if (event.submitter) {
      return event.submitter;
    }

    if (document.activeElement instanceof HTMLInputElement && document.activeElement.type === "submit") {
      return document.activeElement;
    }

    return null;
  }

  function bytesToBase64(bytes) {
    let binary = "";

    bytes.forEach((byte) => {
      binary += String.fromCharCode(byte);
    });

    return btoa(binary);
  }

  function setBusyState(isBusy) {
    submitButtons.forEach((button) => {
      button.disabled = isBusy;
    });
  }

  function showStatus(message, type) {
    if (!statusField) {
      return;
    }

    statusField.textContent = message;
    statusField.hidden = !message;
    statusField.dataset.state = type;
  }

  async function deriveCommentKey(email, password, salt) {
    const keyMaterial = await window.crypto.subtle.importKey(
      "raw",
      encoder.encode(`${email}\n${password}`),
      "PBKDF2",
      false,
      ["deriveKey"]
    );

    return window.crypto.subtle.deriveKey(
      {
        name: "PBKDF2",
        hash: "SHA-256",
        salt,
        iterations: PBKDF2_ITERATIONS
      },
      keyMaterial,
      {
        name: "AES-GCM",
        length: 256
      },
      false,
      ["encrypt"]
    );
  }

  async function encryptComment(comment, email, password) {
    const salt = window.crypto.getRandomValues(new Uint8Array(16));
    const iv = window.crypto.getRandomValues(new Uint8Array(12));
    const key = await deriveCommentKey(email, password, salt);
    const encryptedBuffer = await window.crypto.subtle.encrypt(
      {
        name: "AES-GCM",
        iv
      },
      key,
      encoder.encode(comment)
    );

    return {
      ciphertext: bytesToBase64(new Uint8Array(encryptedBuffer)),
      metadata: `enc-v1|${PBKDF2_ITERATIONS}|${bytesToBase64(salt)}|${bytesToBase64(iv)}`
    };
  }

  form.addEventListener("submit", async (event) => {
    const submitter = findSubmitter(event);
    const action = submitter?.value ?? "";

    if (skipNextEncryption) {
      skipNextEncryption = false;
      return;
    }

    if (!ACTIONS_WITH_ENCRYPTION.has(action)) {
      metadataField.value = "";
      showStatus("", "info");
      return;
    }

    const comment = commentField.value;

    if (!comment.trim()) {
      metadataField.value = "";
      showStatus("", "info");
      return;
    }

    if (!window.crypto || !window.crypto.subtle) {
      event.preventDefault();
      showStatus("Nettleseren støtter ikke klientside-kryptering av kommentar.", "error");
      return;
    }

    const email = emailField.value.trim();
    const password = passwordField.value;
    const commentBytes = encoder.encode(comment);

    if (!email || !password) {
      event.preventDefault();
      showStatus("E-post og passord må fylles ut før kommentar kan krypteres.", "error");
      return;
    }

    if (commentBytes.length > MAX_COMMENT_BYTES) {
      event.preventDefault();
      showStatus("Kommentar er for lang til å krypteres i steg 6. Maks 700 byte akkurat nå.", "error");
      return;
    }

    event.preventDefault();
    setBusyState(true);

    try {
      const { ciphertext, metadata } = await encryptComment(comment, email, password);

      commentField.value = ciphertext;
      metadataField.value = metadata;
      showStatus("Kommentar krypteres i nettleseren før innsending.", "info");
      setBusyState(false);
      skipNextEncryption = true;

      if (typeof form.requestSubmit === "function" && submitter) {
        form.requestSubmit(submitter);
      } else {
        form.submit();
      }
    } catch (error) {
      console.error("Kryptering feilet", error);
      showStatus("Kryptering av kommentar feilet. Prøv igjen.", "error");
    } finally {
      setBusyState(false);
    }
  });
}
// slutt: Klientside-kryptering av kommentar før innsending - oppfyller F1 (privat kommentar) og NF7 (kryptering og nøkkelhåndtering i klient) (person 3)
