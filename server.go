package zeitnow

import (
	"encoding/xml"
	"fmt"
	"net/http"
	"appengine"
	"appengine/urlfetch"
	"io/ioutil"
)

func wikiWords(w http.ResponseWriter, r *http.Request) {
	type Page struct {
		Title	string	`xml:"title"`
	}
	
	type Result struct {
		XMLName	xml.Name `xml:"pages"`
		Type	string	 `xml:"type,attr"`
		Page	[]Page	 `xml:"page"`
	}

	c := appengine.NewContext(r)
	client := urlfetch.Client(c)

	resp, err := client.Get("http://www.trendingtopics.org/pages.xml")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	body, err := ioutil.ReadAll(resp.Body)
	resp.Body.Close()

	v := Result{}
	err = xml.Unmarshal([]byte(body), &v)

	if err != nil {
		fmt.Fprintf(w, "No marsh: %v", err)
	}
	fmt.Fprintf(w, "%v", v)
	return
}

func init() {
	http.HandleFunc("/", handler)
}

func handler(w http.ResponseWriter, r *http.Request) {
	wikiWords(w, r)
}
