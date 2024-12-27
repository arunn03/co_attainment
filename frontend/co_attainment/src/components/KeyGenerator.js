import React, { useState } from 'react';
import forge from 'node-forge';

function GenerateKeys({ username }) {
  const [publicKey, setPublicKey] = useState(null);
  const [privateKey, setPrivateKey] = useState(null);

  const generateKeys = () => {
    const { privateKey, publicKey } = forge.pki.rsa.generateKeyPair({ bits: 2048, e: 0x10001 });

    // Convert keys to PEM format
    const privatePem = forge.pki.privateKeyToPem(privateKey);
    const publicPem = forge.pki.publicKeyToPem(publicKey);

    // Save or set the keys as needed
    setPrivateKey(privatePem);
    setPublicKey(publicPem);

    // Optionally download the private key file
    const blob = new Blob([privatePem], { type: 'application/x-pem-file' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${username}_private_key.pem`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <button onClick={generateKeys}>Generate Keys</button>
      {publicKey && (
        <div>
          <h3>Public Key:</h3>
          <textarea value={publicKey} readOnly rows={10} cols={50} />
        </div>
      )}
      {privateKey && (
        <div>
          <h3>Private Key:</h3>
          <textarea value={privateKey} readOnly rows={10} cols={50} />
        </div>
      )}
    </div>
  );
}

export default GenerateKeys;