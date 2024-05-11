import { encryptPaste } from './crypto.coffee'

handleFormSubmission = (event) ->
  event.preventDefault()

  formData = new FormData @
  pasteTitle = formData.get 'pasteName'
  pasteTitle = 'Unnamed' if pasteTitle.length is 0
  pasteText = formData.get 'pasteText'

  e2eeChecked = formData.get('e2ee')?

  if e2eeChecked
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
        window.location.href = if e2eeChecked then "#{response.url}?k=#{keyEncoded}" else response.url
      if response.status is 401
        alert('Nuh-uh!')
    .catch (error) ->
      console.error error

document.addEventListener 'DOMContentLoaded', ->
  newPasteForm = document.getElementById 'newPasteForm'
  newPasteForm?.addEventListener 'submit', handleFormSubmission
