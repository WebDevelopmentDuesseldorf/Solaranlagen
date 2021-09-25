import React from 'react';
import { Link } from 'react-router-dom'


function Footer(){ 
    return (
        <footer className="py-5 ">
            <div className="container">
                <div className="row">
                    <div className="col-md-4">
                        <h6>The Mission</h6>
                        <hr />
                     
                        <p>
                            Consequat laborum id nisi laboris ex in fugiat aute. Sit nostrud culpa ut magna ipsum deserunt duis. Ut labore voluptate consectetur nulla elit ullamco deserunt fugiat sint occaecat eu. Occaecat Lorem aliquip enim cupidatat commodo esse occaecat nisi anim id ad in nisi consectetur. Amet Lorem exercitation ullamco exercitation Lorem sunt occaecat. Fugiat mollit sint voluptate fugiat dolore cupidatat cillum nulla proident cupidatat voluptate enim velit ullamco. Velit non proident enim dolor esse eiusmod culpa cillum anim id occaecat dolor.
                        </p>
                    </div>
                    <div className="col-md-4">
                        <h6>Quick Links</h6>
                        <hr />
                        <div><Link to="/home" className="text-decoration-none"> Home</Link></div>
                        <div><Link to="/overview" className="text-decoration-none"> Overview</Link></div>
                        <div><Link to="/about" className="text-decoration-none"> About</Link></div>
                    </div>
                    <div className="col-md-4">
                    <h6>Contact Us</h6>
                    <hr />
                    <div><p>Solaranlagen GmbH - Umweltstr. 2030 - 40227 Duesseldorf</p></div>
                    <div><p>Tel: 0211 / 543723</p></div>
                    <div><p>Email: info@solaranlagen.de</p></div>
                    <div><p><Link to="/contact">Contact Us Form</Link></p></div>
                    
                </div>



                </div>
            </div>
        </footer>
    )
}

export default Footer