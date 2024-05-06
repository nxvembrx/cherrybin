import { encryptPaste } from './crypto.coffee'
# key = randomBytes 32
# nonce = randomBytes 24
# chacha = xchacha20poly1305 key, nonce
# data = utf8ToBytes "hello, noble"
# ciphertext = chacha.encrypt data

# console.log ciphertext

# data_ = chacha.decrypt ciphertext

# console.log bytesToUtf8 data_

handleFormSubmission = (event) ->
  event.preventDefault()

  formData = new FormData @
  pasteTitle = formData.get 'pasteName'
  pasteTitle = 'Unnamed' if pasteTitle.length is 0
  pasteText = formData.get 'pasteText'

  {
    keyEncoded
    titleEncryped
    textEncrypted
  } = encryptPaste pasteTitle, pasteText

  formData.set 'pasteName', titleEncryped
  formData.set 'pasteText', textEncrypted

  fetch(
    @action
    method: @method
    body: formData
  )
    .then (response) ->
      if response.ok
        window.location.href = "#{response.url}?k=#{keyEncoded}"
    .catch (error) ->
      console.error error

document.addEventListener 'DOMContentLoaded', ->
  newPasteForm = document.getElementById 'newPasteForm'
  newPasteForm?.addEventListener 'submit', handleFormSubmission

export { pasteToFile, processEncryptedPaste } from './pasteActions.coffee'
