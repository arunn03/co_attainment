import CryptoJS from "crypto-js";
// import Fernet from "fernet";

export const decryptContent = (encryptedContent, key) => {
  const bytes = CryptoJS.AES.decrypt(encryptedContent, key);
  // console.log(bytes.toString());
  return bytes;

  // const fernet = new Fernet({ secret: key });

  // try {
  //   // Decrypt the token
  //   const decryptedMessage = fernet.decode(encryptedContent);
  //   return decryptedMessage;
  // } catch (error) {
  //   console.error("Decryption failed:", error);
  //   return null;
  // }
};
