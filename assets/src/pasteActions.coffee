pasteToFile = (title, contents) ->
  fileContents = """
    #{title}

    #{contents}
    """
  url = URL.createObjectURL(
    new Blob [fileContents], type: "text/plain;charset=utf-8"
  )
  link = document.createElement "a"
  link.href = url
  link.download = "#{title}.txt"
  link.click()
  URL.revokeObjectURL link

export { pasteToFile }
