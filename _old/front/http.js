const base_url = "http://0.0.0.0"


const request = async(path, body_json) => {
  const options = {
    method: 'post',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body_json)
  };
  const response = await fetch(`${base_url}/${path}`, options);
  return response;
}


const post = async(path, body_json) => {
  return await request(path, body_json).then( async (response) => {
    return await response.json()
  })
}


export {
  request,
  post,
  base_url,
}
