import React from 'react';
import Footer from '../inc/Footer'

class Contact extends React.Component{
    render(){ 
        return( 
        <div>
            <article className="py-5">
                <div className="container">
                <div className="row">
                <div className="col-md-8">
                <iframe title="googleMapsContact" src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d385076.590923317!2d28.68881403281249!3d41.060010800000015!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x14cab73b72c0004f%3A0x9ab4ac65e093a293!2sTech%20Labs!5e0!3m2!1sde!2sde!4v1632505362098!5m2!1sde!2sde" width="100%" height="450" allowfullscreen="" loading="lazy"></iframe>
                </div>
                <div className="col-md-4">
                <div className="card shadow">
                <div className="card-body">
                    <h3>Contact Us</h3>
                    <div className="underline mb-3"></div>
                        <form>
                            <label for="">Name</label>
                            <input type="text" placeholder="Enter your Name" className="form-control mb-3" />
                            <label for="">E-Mail</label>
                            <input type="text" placeholder="Enter your E-Mail-Adress" className="form-control mb-3" />
                            <label for="">Message</label>
                            <textarea rows="5" placeholder="Your Message" className="form-control mb-3"></textarea>
                            <button type="submit" className="btn w-100 button">Submit</button>
                        </form> 
                        </div>
                        </div>
                </div>
                </div>
                </div>
            
            </article>  
            
            <Footer />
           
            </div>
        );
    }
}


export default Contact; 