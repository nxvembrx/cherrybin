import { xchacha20poly1305 } from '@noble/ciphers/chacha'
import {
  utf8ToBytes
  bytesToUtf8
  bytesToHex
  hexToBytes
} from '@noble/ciphers/utils'
import { randomBytes, managedNonce } from '@noble/ciphers/webcrypto'

encryptPaste = (title, text) ->
  key = randomBytes 32
  keyEncoded = bytesToHex key
  chacha = initChacha key

  titleEncryped = bytesToHex chacha.encrypt utf8ToBytes title
  textEncrypted = bytesToHex chacha.encrypt utf8ToBytes text

  { keyEncoded, titleEncryped, textEncrypted }

decryptPaste = (title, text) ->
  try
    key = hexToBytes new URLSearchParams(window.location.search).get 'k'
    decryptedTitle = bytesToUtf8 initChacha(key).decrypt hexToBytes title
    decryptedText = bytesToUtf8 initChacha(key).decrypt hexToBytes text
  catch error
    console.log error

  { decryptedTitle, decryptedText }

initChacha = (key) ->
  chacha = managedNonce(xchacha20poly1305) key

export { encryptPaste, decryptPaste }
